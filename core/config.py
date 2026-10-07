"""Konfigurasi lingkungan dan kunci API untuk RAG Mahasiswa."""
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Muat file .env dari root proyek
_base_dir = Path(__file__).resolve().parent.parent
_env_path = _base_dir / ".env" if (_base_dir / ".env").exists() else _base_dir / ".env.example"
load_dotenv(dotenv_path=_env_path, override=True)


# Membaca dari st.secrets (jika di cloud) ATAU os.getenv (jika di lokal laptop)
def get_secret(key: str, default: str = "") -> str:
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        # Menangani situasi jika .streamlit/secrets.toml belum ada saat running lokal
        pass
    return os.getenv(key, default)


# Kunci API & Konfigurasi Supabase
SUPABASE_URL: str = get_secret("SUPABASE_URL", "").strip()
SUPABASE_KEY: str = get_secret("SUPABASE_SERVICE_KEY", "").strip()
GEMINI_API_KEY: str = get_secret("GEMINI_API_KEY", "").strip()
GROQ_API_KEY: str = get_secret("GROQ_API_KEY", "").strip()

# Model AI
LLM_MODEL: str = get_secret("LLM_MODEL", "openai/gpt-oss-120b").strip()
VISION_MODEL: str = get_secret("VISION_MODEL", "gemini-flash-lite-latest").strip()
EMBEDDING_MODEL: str = get_secret("EMBEDDING_MODEL", "models/gemini-embedding-001").strip()

# Validasi variabel penting
_wajib = {
    "SUPABASE_URL": SUPABASE_URL,
    "SUPABASE_SERVICE_KEY": SUPABASE_KEY,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "GROQ_API_KEY": GROQ_API_KEY
}
_kosong = [k for k, v in _wajib.items() if not v]
if _kosong:
    raise RuntimeError(f"Variabel lingkungan berikut wajib diisi di file .env atau st.secrets: {', '.join(_kosong)}")

