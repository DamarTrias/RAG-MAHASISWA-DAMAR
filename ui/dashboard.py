# Tampilan tab Dashboard Utama (Ringkasan aktivitas, statistik materi, dan status sistem).
from typing import Dict, Any
from datetime import datetime
import streamlit as st
from core.db import list_documents
from core.config import LLM_MODEL, EMBEDDING_MODEL, VISION_MODEL


def render(student: Dict[str, Any]) -> None:
    """Merender tab Dashboard Ringkasan Akademik per mahasiswa."""
    docs = list_documents(student["id"])
    total_docs = len(docs)
    total_chunks = sum(
        d.get("chunks", [{}])[0].get("count", 0) if d.get("chunks") else 0
        for d in docs
    )

    # Identifikasi format file yang diunggah
    file_types = set()
    for d in docs:
        ft = d.get("file_type", "").lower()
        if ft:
            file_types.add(ft.replace(".", "").upper())

    # ==========================================
    # 1. KARTU METRIK STATISTIK UTAMA
    # ==========================================
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="📁 Total Dokumen",
            value=f"{total_docs} Berkas",
            delta=f"{len(file_types)} Format" if file_types else "Belum ada materi"
        )

    with col2:
        st.metric(
            label="🧩 Potongan Teks (Chunks)",
            value=f"{total_chunks:,}",
            delta="Terindeks Vektor" if total_chunks > 0 else "0 Indeks"
        )

    with col3:
        st.metric(
            label="🛡️ Status Privasi",
            value="Terisolasi",
            delta=f"NIM: {student['nim']}"
        )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 2. STATUS MATERI TERBARU & PANDUAN KERJA
    # ==========================================
    col_left, col_right = st.columns([1.6, 1.4])

    with col_left:
        st.subheader("📚 Ringkasan Dokumen Materi Anda")
        if not docs:
            st.info(
                "💡 **Belum ada materi yang diunggah.**\n\n"
                "Silakan buka tab **'📁 Dokumen Kuliah'** untuk mengunggah berkas PDF, Word, PPTX, "
                "atau foto materi catatan kuliah pertama Anda."
            )
        else:
            st.caption(f"Menampilkan {min(5, total_docs)} dari {total_docs} dokumen terbaru:")
            for d in docs[:5]:
                count_val = d.get("chunks", [{}])[0].get("count", 0) if d.get("chunks") else 0
                ext_badge = d.get("file_type", "FILE").upper().replace(".", "")
                created_date = d.get("created_at", "")[:10] if d.get("created_at") else "-"

                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="background: #3b82f6; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; margin-right: 8px;">{ext_badge}</span>
                        <strong>{d['name']}</strong>
                        <div style="color: #94a3b8; font-size: 12px; margin-top: 2px;">Diupload: {created_date}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="background: rgba(16, 185, 129, 0.15); color: #10b981; padding: 4px 8px; border-radius: 6px; font-size: 12px; font-weight: 600;">{count_val} chunks</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.subheader("⚡ Navigasi Fitur Cerdas")
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
            <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid #3b82f6; border-radius: 6px; padding: 10px 14px;">
                <strong>📁 1. Dokumen Kuliah</strong><br>
                <small style="color: #94a3b8;">Unggah berkas materi kuliah Anda. Sistem otomatis memecah teks & mengekstrak gambar dengan Vision OCR.</small>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid #10b981; border-radius: 6px; padding: 10px 14px;">
                <strong>💬 2. Chatbot & Sitasi</strong><br>
                <small style="color: #94a3b8;">Ajukan pertanyaan akademik. AI menjawab secara akurat disertai nomor referensi sitasi halaman.</small>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid #f59e0b; border-radius: 6px; padding: 10px 14px;">
                <strong>📝 3. Generatif Soal (Kuis)</strong><br>
                <small style="color: #94a3b8;">Buat latihan soal ujian (Pilihan Ganda & Essay) otomatis dari materi lengkap dengan kunci jawaban.</small>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid #8b5cf6; border-radius: 6px; padding: 10px 14px;">
                <strong>🃏 4. Flashcard Pintar</strong><br>
                <small style="color: #94a3b8;">Kuis kartu bolak-balik untuk melatih daya ingat konsep penting (*active recall*).</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # ==========================================
    # 3. SPESIFIKASI & ARSITEKTUR MESIN AI
    # ==========================================
    with st.expander("⚙️ Spesifikasi Mesin AI & Infrastruktur Sistem", expanded=False):
        c_spec1, c_spec2 = st.columns(2)
        with c_spec1:
            st.markdown(f"""
            * **Model Bahasa Utama (LLM):** `{LLM_MODEL}` (Groq Engine)
            * **Model Vektor Embedding:** `{EMBEDDING_MODEL}` (Gemini 3072-dim)
            * **Model Vision OCR:** `{VISION_MODEL}` (Gemini Multimodal)
            """)
        with c_spec2:
            st.markdown(f"""
            * **Penyimpanan Basis Data:** `Supabase PostgreSQL (Cloud)`
            * **Ekstensi Pencarian Vektor:** `pgvector (Cosine Distance)`
            * **Mekanisme Isolasi Data:** `Multi-Tenant per student_id`
            """)
