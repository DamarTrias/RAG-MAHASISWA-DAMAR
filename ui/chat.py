"""Tampilan tab Chatbot Akademik interaktif dengan sitasi rujukan."""
from typing import Dict, Any
import streamlit as st
from core.rag import answer
from ui.common import pick_document


def render(student: Dict[str, Any]) -> None:
    """Merender tab obrolan chatbot akademik dengan isolasi riwayat per mahasiswa."""
    kiri, kanan = st.columns([1, 2.5])
    chat_key = f"chat_{student['id']}"
    riwayat = st.session_state.setdefault(chat_key, [])

    with kiri:
        st.subheader("Fokus Sumber RAG")
        doc_id = pick_document(student["id"], label="Pilih Dokumen Acuan:", key=f"chat_doc_{student['id']}")
        
        st.markdown("""
        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; margin: 12px 0;">
            <small style="color: #94a3b8;"><strong>💡 Panduan Pertanyaan:</strong><br>
            • "Jelaskan konsep utama materi..."<br>
            • "Ringkas poin-poin penting pada slide..."<br>
            • "Sebutkan kelebihan dan kekurangan..."</small>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ Bersihkan Percakapan", use_container_width=True, key=f"chat_clear_{student['id']}"):
            st.session_state[chat_key] = []
            st.rerun()

    with kanan:
        st.subheader("Ruang Tanya Jawab Akademik")
        
        if not riwayat:
            st.info(f"Halo {student['name']}! Silakan ajukan pertanyaan seputar materi kuliah Anda di bawah.")

        # Tampilkan riwayat obrolan
        for msg in riwayat:
            avatar = "👨‍🎓" if msg["role"] == "user" else "🎓"
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["text"])
                if msg.get("sumber"):
                    with st.expander("📚 Rujukan Sitasi Materi"):
                        for s in msg["sumber"]:
                            st.caption(f"• {s}")

        # Input pengguna
        if user_prompt := st.chat_input("Tanyakan apa saja seputar materi kuliah Anda..."):
            riwayat.append({"role": "user", "text": user_prompt})
            
            with st.spinner("Mencari konteks rujukan & merumuskan jawaban..."):
                try:
                    jawaban, sumber = answer(student["id"], user_prompt, doc_id)
                except Exception as e:
                    jawaban, sumber = f"⚠️ Terjadi kesalahan saat memproses jawaban: {e}", []

            riwayat.append({"role": "assistant", "text": jawaban, "sumber": sumber})
            st.rerun()
