"""Inisialisasi klien model AI (Embeddings, LLM Groq, dan Gemini Vision)."""
from typing import Any, Union
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from core.config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    LLM_MODEL,
    VISION_MODEL,
    EMBEDDING_MODEL
)

# 1. Model Vektor Embedding (Google Gemini)
embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GEMINI_API_KEY
)

# 2. Model Bahasa Utama untuk Penalaran & QA (Groq)
llm = ChatGroq(
    model=LLM_MODEL,
    groq_api_key=GROQ_API_KEY,
    temperature=0.3
)

# 3. Model Khusus Transkripsi Visual & Infografis Gambar (Gemini Multimodal Vision)
vision_llm = ChatGoogleGenerativeAI(
    model=VISION_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0.1
)


def to_text(response: Any) -> str:
    """Mengambil teks bersih dari respons LLM (baik bertipe str maupun list blok pesan)."""
    if not response:
        return ""
    
    if hasattr(response, "content"):
        content = response.content
    else:
        content = response

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for p in content:
            if isinstance(p, str):
                parts.append(p)
            elif isinstance(p, dict):
                parts.append(p.get("text", ""))
        return "".join(parts).strip()

    return str(content).strip()
