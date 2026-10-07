# Membaca dan mengekstrak dokumen multi-format (PDF, PPTX, DOCX, Gambar) beserta label sitasi.
import base64
import io
from typing import List, Tuple, Callable
import fitz  # PyMuPDF
from docx import Document
from pptx import Presentation
from langchain_core.messages import HumanMessage
from core.ai import vision_llm, to_text


def read_image(data: bytes, ext: str) -> List[Tuple[str, str]]:
    # Mengekstrak dan mentranskripsi konten visual materi menggunakan Gemini Vision Multimodal.
    mime = "jpeg" if ext.lower() in ("jpg", "jpeg") else ext.lower()
    b64 = base64.b64encode(data).decode("utf-8")
    
    msg = HumanMessage(content=[
        {
            "type": "text",
            "text": (
                "Transkripsikan semua teks, judul, poin-poin, diagram, bagan, dan rumus pada gambar ini "
                "secara lengkap dan terstruktur dalam Bahasa Indonesia untuk keperluan materi kuliah RAG."
            )
        },
        {
            "type": "image_url",
            "image_url": f"data:image/{mime};base64,{b64}"
        }
    ])
    
    transcription = to_text(vision_llm.invoke([msg]))
    return [(transcription, "Gambar")]


def read_pdf(data: bytes, ext: str) -> List[Tuple[str, str]]:
    # Membaca PDF per halaman dengan OCR Vision otomatis untuk halaman diagram/infografis.
    doc = fitz.open(stream=data, filetype="pdf")
    results: List[Tuple[str, str]] = []

    for i, page in enumerate(doc, 1):
        digital_text = (page.get_text() or "").strip()
        has_images = len(page.get_images()) > 0
        
        # Jika teks digital sangat sedikit (< 100 huruf) dan memiliki gambar, atau halaman visual murni:
        needs_vision = (has_images and len(digital_text) < 100) or (len(digital_text) == 0 and has_images)
        
        if needs_vision:
            try:
                # Render halaman ke gambar berkualitas tinggi (DPI 130) agar OCR presisi
                pix = page.get_pixmap(dpi=130)
                img_bytes = pix.tobytes("png")
                ocr_text, _ = read_image(img_bytes, "png")[0]
                
                # Gabungkan teks judul dengan transkripsi visual gambar
                if digital_text and ocr_text:
                    digital_text = f"{digital_text}\n\n[Transkripsi Visual & Infografis]:\n{ocr_text}"
                elif ocr_text:
                    digital_text = ocr_text
            except Exception as e:
                print(f"[Warning] OCR gagal pada PDF Halaman {i}: {e}")

        if digital_text:
            results.append((digital_text, f"Hal {i}"))

    doc.close()
    return results


def read_pptx(data: bytes, ext: str) -> List[Tuple[str, str]]:
    # Membaca presentasi PowerPoint per slide dengan ekstraksi judul, bentuk, dan tabel.
    prs = Presentation(io.BytesIO(data))
    results: List[Tuple[str, str]] = []

    for i, slide in enumerate(prs.slides, 1):
        slide_parts = []
        
        # Judul slide jika ada
        if slide.shapes.title and slide.shapes.title.text:
            slide_parts.append(f"Judul: {slide.shapes.title.text.strip()}")

        # Kotak teks dan tabel
        for shape in slide.shapes:
            if shape == slide.shapes.title:
                continue
            if shape.has_text_frame and shape.text_frame:
                txt = shape.text_frame.text.strip()
                if txt:
                    slide_parts.append(txt)
            elif shape.has_table:
                for row in shape.table.rows:
                    row_txt = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
                    if row_txt:
                        slide_parts.append(row_txt)

        # Catatan presenter jika ada
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                slide_parts.append(f"[Catatan: {notes}]")

        full_text = "\n".join(slide_parts).strip()
        if full_text:
            results.append((full_text, f"Slide {i}"))

    return results


def read_docx(data: bytes, ext: str) -> List[Tuple[str, str]]:
    # Membaca dokumen Word (.docx) dengan pemisahan per bagian paragraf dan tabel.
    doc = Document(io.BytesIO(data))
    paras = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    results: List[Tuple[str, str]] = []

    # Kelompokkan per 12-15 paragraf sebagai satu bagian logis
    batch_size = 12
    for i in range(0, len(paras), batch_size):
        section_text = "\n".join(paras[i:i + batch_size]).strip()
        if section_text:
            results.append((section_text, f"Bagian {i // batch_size + 1}"))

    # Ekstrak data dari tabel Word jika ada
    for t_idx, table in enumerate(doc.tables, 1):
        tbl_lines = []
        for row in table.rows:
            r_str = " | ".join(c.text.strip() for c in row.cells if c.text.strip())
            if r_str:
                tbl_lines.append(r_str)
        if tbl_lines:
            results.append(("\n".join(tbl_lines), f"Tabel {t_idx}"))

    return results


READERS = {
    "pdf": read_pdf,
    "pptx": read_pptx,
    "docx": read_docx,
    "png": read_image,
    "jpg": read_image,
    "jpeg": read_image,
}


def load_file(filename: str, data: bytes) -> Tuple[List[Tuple[str, str]], str]:
    # Mendeteksi ekstensi file dan memuat seluruh bagian teks beserta label sitasi.
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in READERS:
        supported = ", ".join(f".{k}" for k in READERS.keys())
        raise ValueError(f"Format .{ext} tidak didukung. Format yang didukung: {supported}")
    
    extracted_pages = READERS[ext](data, ext)
    return extracted_pages, ext
