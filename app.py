"""Aplikasi RAG Mahasiswa AI - Portal Belajar Cerdas Terisolasi Per Mahasiswa."""
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="RAG Mahasiswa AI - Portal Belajar",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from core.db import list_students
from ui import chat, dashboard, documents, flashcards, quiz

# Cek apakah mahasiswa sudah login
if "user" not in st.session_state or st.session_state["user"] is None:
    from ui import auth
    auth.render()
    st.stop()  # Berhenti di sini jika belum login

# Jika sudah login, ambil data mahasiswa aktif dari sesi
student = st.session_state["user"]


# ---------- Header & Pemilihan Akun Mahasiswa ----------
col_header, col_account = st.columns([2.7, 2.3], vertical_alignment="center")

with col_header:
    st.title("🎓 RAG Mahasiswa AI")
    st.caption("Sistem Belajar Cerdas Terisolasi Per Mahasiswa")

with col_account:
    initial_char = student['name'][0].upper() if student.get('name') else 'M'
    col_user_info, col_btn_logout = st.columns([2.6, 1.2], vertical_alignment="center")
    with col_user_info: 
        st.markdown(f"""
        <div style="
            display: flex;
            align-items: center;
            gap: 12px;
            background: rgba(255, 255, 255, 0.04);
            border: 1.5px solid rgba(255, 255, 255, 0.18);
            border-radius: 12px;
            padding: 8px 14px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        ">
            <div style="
                background: linear-gradient(135deg, #3b82f6, #2563eb);
                color: #ffffff;
                width: 38px;
                height: 38px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 17px;
                font-weight: 700;
                flex-shrink: 0;
            ">
                {initial_char}
            </div>
            <div style="min-width: 0;">
                <div style="font-size: 15px; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    {student['name']}
                </div>
                <div style="font-size: 12.5px; font-weight: 600; color: #38bdf8; margin-top: 1px;">
                    NIM: <span style="color: #cbd5e1; font-weight: 600;">{student['nim']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_btn_logout:
        if st.button("🚪 Keluar", type="secondary", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()


# Banner Privasi & Isolasi Data
st.success(
    f"🛡️ **Privasi Terisolasi** — Anda login sebagai **{student['name']} ({student['nim']})**. "
    "Semua dokumen, chat, kuis, dan flashcard hanya dapat diakses oleh Anda. Mahasiswa lain tidak bisa melihat data Anda."
)

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ---------- 5 Tab Fitur Utama ----------
tab_dash, tab_docs, tab_chat, tab_quiz, tab_cards = st.tabs([
    "🏠 Dashboard Ringkasan",
    "📁 Dokumen Kuliah",
    "💬 Chatbot & Sitasi",
    "📝 Generatif Soal (Kuis)",
    "🃏 Flashcard Pintar"
])

with tab_dash:
    dashboard.render(student)

with tab_docs:
    documents.render(student)

with tab_chat:
    chat.render(student)

with tab_quiz:
    quiz.render(student)

with tab_cards:
    flashcards.render(student)
