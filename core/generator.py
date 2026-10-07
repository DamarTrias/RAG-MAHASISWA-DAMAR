"""Generator soal latihan ujian dan flashcard terisolasi dari materi mahasiswa."""
import json
import re
from typing import List, Optional
from pydantic import BaseModel, Field

from core.ai import llm, to_text
from core.db import db


class Soal(BaseModel):
    pertanyaan: str = Field(description="Teks butir soal pertanyaan")
    pilihan: List[str] = Field(
        default_factory=list,
        description="4 opsi pilihan ganda berawalan 'A. ', 'B. ', 'C. ', 'D. '. Kosongkan jika tipe soal adalah Essay."
    )
    jawaban: str = Field(description="Kunci jawaban benar atau poin jawaban essay")
    pembahasan: str = Field(description="Penjelasan akademis mengapa jawaban tersebut benar")
    sumber: str = Field(description="Sitasi sumber materi, contoh: Pertemuan_10.pptx (Slide 3)")


class Kuis(BaseModel):
    soal: List[Soal]


class Kartu(BaseModel):
    depan: str = Field(description="Pertanyaan atau istilah kunci konsep di bagian depan kartu")
    belakang: str = Field(description="Jawaban atau penjelasan ringkas dan padat di bagian belakang kartu")


class SetKartu(BaseModel):
    kartu: List[Kartu]


def extract_json_from_text(text: str) -> dict:
    """Mengekstrak dan mem-parsing blok JSON dari respon teks model secara aman."""
    # Bersihkan markdown ```json ... ``` jika ada
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)

    # Cari blok kurung kurawal terluar { ... }
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    return json.loads(cleaned)


def get_context(student_id: str, doc_id: Optional[str] = None, limit: int = 15) -> str:
    """Mengambil cuplikan materi milik mahasiswa untuk dijadikan bahan penyusunan soal atau flashcard."""
    query = db.table("chunks").select("content, citation").eq("student_id", student_id)
    if doc_id:
        query = query.eq("document_id", doc_id)
    
    rows = query.limit(limit).execute().data
    if not rows:
        raise ValueError("Belum ada materi yang diunggah untuk profil ini. Silakan unggah dokumen terlebih dahulu.")
    
    return "\n\n".join(f"({r['citation']})\n{r['content']}" for r in rows)


def make_quiz(student_id: str, doc_id: Optional[str], jumlah: int, level: str, tipe: str) -> List[Soal]:
    """Menghasilkan paket soal kuis (Pilihan Ganda atau Essay) dalam mode JSON murni (bebas dari error tool-use)."""
    context = get_context(student_id, doc_id)
    
    if tipe == "Pilihan Ganda":
        aturan = "Pilihan Ganda dengan 4 opsi pilihan (A, B, C, D) yang jelas di dalam list 'pilihan'"
        format_contoh = '{"pertanyaan": "...", "pilihan": ["A. ...", "B. ...", "C. ...", "D. ..."], "jawaban": "A. ...", "pembahasan": "...", "sumber": "..."}'
    else:
        aturan = "Essay analisis mendalam. Bagian 'pilihan' WAJIB KOSONG [], dan 'jawaban' berupa poin kunci jawaban ideal"
        format_contoh = '{"pertanyaan": "...", "pilihan": [], "jawaban": "...", "pembahasan": "...", "sumber": "..."}'

    prompt = (
        f"Anda adalah dosen pembuat soal ujian. Buatlah tepat {jumlah} butir soal berformat {aturan}, "
        f"dengan tingkat kesulitan '{level}', dalam Bahasa Indonesia, "
        f"dan HANYA bersumber dari materi kuliah berikut:\n\n{context}\n\n"
        "ATURAN OUTPUT:\n"
        "Kembalikan HANYA teks JSON valid tanpa format markdown tambahan. Bentuk skema JSON:\n"
        "{\n"
        f'  "soal": [\n    {format_contoh}\n  ]\n'
        "}"
    )

    # Panggil LLM secara langsung (menggunakan text generation murni)
    response = llm.invoke(prompt)
    raw_text = to_text(response)

    try:
        parsed_json = extract_json_from_text(raw_text)
        kuis_obj = Kuis.model_validate(parsed_json)
        return kuis_obj.soal
    except Exception as err:
        raise RuntimeError(f"Gagal mem-parsing format soal dari model: {err}. Coba buat soal lagi.")


def make_flashcards(student_id: str, doc_id: Optional[str], jumlah: int) -> List[Kartu]:
    """Menghasilkan set flashcard (Konsep/Tanya -> Jawab) dalam mode JSON murni."""
    context = get_context(student_id, doc_id)
    prompt = (
        f"Buatlah {jumlah} buah flashcard belajar cerdas (sisi depan: pertanyaan atau istilah kunci, "
        f"sisi belakang: definisi atau jawaban padat) dalam Bahasa Indonesia dari materi kuliah berikut:\n\n{context}\n\n"
        "ATURAN OUTPUT:\n"
        "Kembalikan HANYA teks JSON valid:\n"
        "{\n"
        '  "kartu": [\n'
        '    {"depan": "Pertanyaan atau konsep...", "belakang": "Penjelasan ringkas..."}\n'
        '  ]\n'
        "}"
    )

    response = llm.invoke(prompt)
    raw_text = to_text(response)

    try:
        parsed_json = extract_json_from_text(raw_text)
        set_kartu = SetKartu.model_validate(parsed_json)
        return set_kartu.kartu
    except Exception as err:
        raise RuntimeError(f"Gagal mem-parsing format flashcard: {err}. Coba buat flashcard lagi.")
