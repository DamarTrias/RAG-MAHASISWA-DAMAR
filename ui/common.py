# Komponen antarmuka yang digunakan berulang pada berbagai tab.
from typing import Optional
import streamlit as st
from core.db import list_documents


def pick_document(student_id: str, label: str = "Sumber Dokumen", key: Optional[str] = None) -> Optional[str]:
    # Dropdown pemilihan filter dokumen materi. Mengembalikan ID dokumen terpilih (None jika memilih semua dokumen).
    docs_data = list_documents(student_id)
    docs_map = {d["name"]: d["id"] for d in docs_data}
    
    options = ["Semua Dokumen Saya"] + list(docs_map.keys())
    selected_name = st.selectbox(label, options=options, key=key)
    
    return docs_map.get(selected_name)
