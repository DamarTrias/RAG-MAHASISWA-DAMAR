"""Aplikasi RAG Mahasiswa AI - Portal Belajar Cerdas Terisolasi Per Mahasiswa."""
import streamlit as st

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="RAG Mahasiswa AI - Portal Belajar",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Sembunyikan Header, Toolbar Fork/GitHub, Menu, Footer, dan Widget Badge Streamlit
st.markdown("""
<style>
    header[data-testid="stHeader"], 
    [data-testid="stHeader"], 
    .stAppHeader, 
    [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
    }

    
    [data-testid="stToolbar"], 
    #MainMenu {
        display: none !important;
        visibility: hidden !important;
    }

    
    footer {
        display: none !important;
        visibility: hidden !important;
    }

    
    [data-testid="stStatusWidget"], 
    div[class*="StatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }

    [data-testid="manage-app-button"], 
    [class*="viewerBadge"], 
    div[class*="viewerBadge"] {
        display: none !important;
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)




from core.db import list_students
from ui import chat, documents, flashcards, quiz

# Cek apakah mahasiswa sudah login
if "user" not in st.session_state or st.session_state["user"] is None:
    from ui import auth
    auth.render()
    st.stop() 

student = st.session_state["user"]


# ---------- Header & Pemilihan Akun Mahasiswa ----------
col_header, col_account = st.columns([3, 2])

with col_header:
    st.title("🎓 RAG Mahasiswa AI")
    st.caption("Sistem Belajar Cerdas Terisolasi Per Mahasiswa")

with col_account:
    col_user_info, col_btn_logout = st.columns([2.2, 1])
    with col_user_info:
        st.markdown(f"**👤 {student['name']}**")
        st.caption(f"NIM: {student['nim']}")
    with col_btn_logout:
        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Keluar", type="secondary", use_container_width=True):
            st.session_state["user"] = None
            st.rerun()


# Banner Privasi & Isolasi Data
st.success(
    f"🛡️ **Privasi Terisolasi** — Anda login sebagai **{student['name']} ({student['nim']})**. "
    "Semua dokumen, chat, kuis, dan flashcard hanya dapat diakses oleh Anda. Mahasiswa lain tidak bisa melihat data Anda."
)

st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

# ---------- 4 Tab Fitur Utama ----------
tab_docs, tab_chat, tab_quiz, tab_cards = st.tabs([
    "📁 Dokumen Kuliah",
    "💬 Chatbot & Sitasi",
    "📝 Generatif Soal (Kuis)",
    "🃏 Flashcard Pintar"
])

with tab_docs:
    documents.render(student)

with tab_chat:
    chat.render(student)

with tab_quiz:
    quiz.render(student)

with tab_cards:
    flashcards.render(student)
