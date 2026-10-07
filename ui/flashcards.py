"""Tampilan tab Flashcard Pintar untuk metode belajar spaced repetition."""
from typing import Dict, Any
import streamlit as st
from core.generator import make_flashcards
from ui.common import pick_document


def render(student: Dict[str, Any]) -> None:
    """Merender antarmuka flashcard interaktif per mahasiswa."""
    kiri, kanan = st.columns([1, 2])
    cards_key = f"cards_{student['id']}"
    idx_key = f"card_idx_{student['id']}"
    flip_key = f"card_flip_{student['id']}"

    if idx_key not in st.session_state:
        st.session_state[idx_key] = 0
    if flip_key not in st.session_state:
        st.session_state[flip_key] = False

    with kiri:
        st.subheader("Buat Flashcard")
        st.caption("Ekstraksi konsep kunci secara otomatis dari dokumen materi.")
        
        doc_id = pick_document(student["id"], label="Pilih Dokumen Sumber:", key=f"cards_doc_{student['id']}")
        jumlah = st.selectbox("Jumlah Kartu:", [5, 10, 15], key=f"cards_qty_{student['id']}")
        
        if st.button("✨ Buat Flashcard Baru", type="primary", use_container_width=True, key=f"cards_btn_{student['id']}"):
            with st.spinner("Mengekstrak konsep & membuat flashcard..."):
                try:
                    cards = make_flashcards(student["id"], doc_id, jumlah)
                    st.session_state[cards_key] = cards
                    st.session_state[idx_key] = 0
                    st.session_state[flip_key] = False
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal membuat flashcard: {e}")

    with kanan:
        st.subheader("Flashcard Pintar")
        kartu_list = st.session_state.get(cards_key)
        
        if not kartu_list:
            st.info("Pilih dokumen dan klik 'Buat Flashcard Baru' untuk mulai belajar.")
            return

        cur_idx = st.session_state[idx_key]
        if cur_idx >= len(kartu_list):
            cur_idx = 0
            st.session_state[idx_key] = 0

        card = kartu_list[cur_idx]
        is_flipped = st.session_state[flip_key]

        # Tampilan Kartu Interaktif
        card_title = "💡 JAWABAN & PENJELASAN" if is_flipped else "❓ PERTANYAAN / KONSEP"
        card_content = card.belakang if is_flipped else card.depan
        card_color = "#10b981" if is_flipped else "#3b82f6"

        st.markdown(f"""
        <div style="background: rgba(255,255,255,0.03); border: 2px solid {card_color}; border-radius: 16px; padding: 36px 24px; min-height: 200px; text-align: center; margin: 16px 0;">
            <div style="font-size: 11px; font-weight: 800; color: {card_color}; letter-spacing: 0.08em; margin-bottom: 12px;">{card_title}</div>
            <div style="font-size: 18px; font-weight: 600; line-height: 1.5; color: #f8fafc;">{card_content}</div>
        </div>
        """, unsafe_allow_html=True)

        # Kontrol Navigasi & Flip
        c_prev, c_flip, c_next = st.columns([1, 1.5, 1])
        
        with c_prev:
            if st.button("⬅️ Sebelumnya", use_container_width=True, disabled=(cur_idx == 0)):
                st.session_state[idx_key] = max(0, cur_idx - 1)
                st.session_state[flip_key] = False
                st.rerun()

        with c_flip:
            flip_label = "🔄 Balik ke Pertanyaan" if is_flipped else "🔄 Balik Lihat Jawaban"
            if st.button(flip_label, use_container_width=True, type="primary"):
                st.session_state[flip_key] = not is_flipped
                st.rerun()

        with c_next:
            if st.button("Berikutnya ➡️", use_container_width=True, disabled=(cur_idx == len(kartu_list) - 1)):
                st.session_state[idx_key] = min(len(kartu_list) - 1, cur_idx + 1)
                st.session_state[flip_key] = False
                st.rerun()

        st.caption(f"<div style='text-align: center; margin-top: 10px;'>Kartu {cur_idx + 1} dari {len(kartu_list)}</div>", unsafe_allow_html=True)
