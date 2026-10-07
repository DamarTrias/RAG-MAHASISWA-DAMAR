# Tampilan tab manajemen dokumen materi kuliah (Upload & Hapus terisolasi).
from typing import Dict, Any
import streamlit as st
from core.db import delete_document, list_documents
from core.rag import ingest


def render(student: Dict[str, Any]) -> None:
    # Merender tab unggah materi kuliah dan daftar dokumen aktif.
    kiri, kanan = st.columns([1.1, 1.9])

    with kiri:
        st.subheader("Unggah Materi Kuliah")
        st.caption("Mendukung format: PDF, PPTX, DOCX, dan Gambar.")
        
        files = st.file_uploader(
            "Pilih file materi:",
            accept_multiple_files=True,
            type=["pdf", "pptx", "docx", "png", "jpg", "jpeg"],
            key=f"uploader_{student['id']}"
        )
        
        if st.button("🚀 Proses Dokumen", type="primary", key=f"btn_process_{student['id']}") and files:
            for f in files:
                with st.spinner(f"Memproses & menganalisis {f.name}..."):
                    try:
                        chunk_count = ingest(student["id"], f.name, f.read())
                        st.success(f"✅ {f.name}: {chunk_count} chunk berhasil diekstrak dan disimpan.")
                    except Exception as e:
                        st.error(f"❌ {f.name}: {e}")
            st.rerun()

    with kanan:
        st.subheader("Daftar Dokumen Anda")
        st.caption(f"Milik: {student['name']}")
        
        docs = list_documents(student["id"])
        if not docs:
            st.info("Belum ada dokumen yang diunggah untuk akun mahasiswa ini.")
            return

        for d in docs:
            c_format, c_name, c_chunk, c_del = st.columns([1, 4, 2, 1])
            
            with c_format:
                st.code(d.get("file_type", "FILE").upper())
            with c_name:
                st.write(f"**{d['name']}**")
            with c_chunk:
                count_val = d.get("chunks", [{}])[0].get("count", 0) if d.get("chunks") else 0
                st.caption(f"{count_val} chunk")
            with c_del:
                if st.button("🗑️ Hapus", key=f"del_{d['id']}", help="Hapus dokumen ini"):
                    delete_document(student["id"], d["id"])
                    st.success(f"Dokumen {d['name']} berhasil dihapus.")
                    st.rerun()
            
            st.markdown("<hr style='margin: 8px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
