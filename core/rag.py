"""Alur RAG: Ingestion (chunking + embedding) -> Retrieval -> Generation dengan Sitasi."""
from typing import List, Tuple, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.ai import embeddings, llm, to_text
from core.db import db
from core.loader import load_file

# Pemotong teks dengan overlap kontekstual
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)


def ingest(student_id: str, filename: str, data: bytes) -> int:
    """Memproses file, membuat embedding vektor, dan menyimpannya secara terisolasi per student_id."""
    pages, ext = load_file(filename, data)
    texts: List[str] = []
    citations: List[str] = []

    for text, label in pages:
        for part in splitter.split_text(text):
            cleaned = part.strip()
            if cleaned:
                texts.append(cleaned)
                citations.append(f"{filename} ({label})")

    if not texts:
        raise ValueError("Tidak ada teks atau gambar materi yang dapat dibaca dari file ini.")

    # Hitung vektor embedding untuk seluruh chunk
    vectors = embeddings.embed_documents(texts)

    # Simpan metadata dokumen induk
    doc_res = db.table("documents").insert({
        "student_id": student_id,
        "name": filename,
        "file_type": ext
    }).execute()
    
    if not doc_res.data:
        raise RuntimeError("Gagal menyimpan metadata dokumen ke Supabase.")
    
    doc_id = doc_res.data[0]["id"]

    # Simpan rekaman chunk ke Supabase dalam batch (50 baris per batch)
    rows = [
        {
            "document_id": doc_id,
            "student_id": student_id,
            "content": t,
            "citation": c,
            "embedding": v
        }
        for t, c, v in zip(texts, citations, vectors)
    ]

    for i in range(0, len(rows), 50):
        db.table("chunks").insert(rows[i:i + 50]).execute()

    return len(rows)


def retrieve(student_id: str, question: str, doc_id: Optional[str] = None, k: int = 5) -> List[Dict[str, Any]]:
    """Mencari potongan dokumen paling relevan via Supabase match_chunks (Dibatasi per student_id)."""
    if not question.strip():
        return []
    
    query_vec = embeddings.embed_query(question)
    params = {
        "query_embedding": query_vec,
        "p_student_id": student_id,
        "p_document_id": doc_id,
        "match_count": k
    }
    
    res = db.rpc("match_chunks", params).execute()
    return res.data or []


def answer(student_id: str, question: str, doc_id: Optional[str] = None) -> Tuple[str, List[str]]:
    """Menjawab pertanyaan mahasiswa dengan sitasi rujukan yang akurat."""
    hits = retrieve(student_id, question, doc_id=doc_id, k=5)
    if not hits:
        return "Materi terkait tidak ditemukan dalam dokumen Anda. Pastikan Anda telah mengunggah dokumen materi terlebih dahulu.", []

    # Susun konteks bernomor untuk perujukan
    context = "\n\n".join(
        f"[{i}] ({h['citation']})\n{h['content']}"
        for i, h in enumerate(hits, 1)
    )

    prompt = (
        "Anda adalah asisten akademik cerdas. Jawab pertanyaan mahasiswa secara ramah, jelas, "
        "dan HANYA berdasarkan konteks materi yang disediakan di bawah ini.\n\n"
        "ATURAN PENTING:\n"
        "1. Tulis nomor referensi seperti [1], [2] di bagian kalimat yang merujuk pada informasi tersebut.\n"
        "2. Jika jawaban tidak ada pada konteks, sampaikan dengan jujur bahwa informasi belum tercantum di materi.\n"
        "3. Gunakan bahasa Indonesia yang baik dan terstruktur rapi dengan markdown.\n\n"
        f"KONTEKS MATERI:\n{context}\n\n"
        f"PERTANYAAN: {question}\n\n"
        "JAWABAN:"
    )

    raw_answer = to_text(llm.invoke(prompt))
    source_list = [f"[{i}] {h['citation']}" for i, h in enumerate(hits, 1)]
    return raw_answer, source_list
