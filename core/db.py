# Lapisan akses basis data Supabase terisolasi per mahasiswa.
from typing import List, Dict, Any
from supabase import create_client, Client
from core.config import SUPABASE_URL, SUPABASE_KEY

# Inisialisasi klien Supabase
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def list_students() -> List[Dict[str, Any]]:
    # Mengambil daftar seluruh akun mahasiswa dari basis data.
    res = db.table("students").select("*").order("nim").execute()
    return res.data or []


def list_documents(student_id: str) -> List[Dict[str, Any]]:
    # Mengambil daftar dokumen milik satu mahasiswa tertentu beserta jumlah potongan chunk (Terisolasi).
    res = (
        db.table("documents")
        .select("*, chunks(count)")
        .eq("student_id", student_id)
        .order("created_at", desc=True)
        .execute()
    )
    return res.data or []


def delete_document(student_id: str, doc_id: str) -> None:
    # Menghapus dokumen dan seluruh chunk miliknya secara permanen (Terisolasi per student_id).
    db.table("documents").delete().eq("id", doc_id).eq("student_id", student_id).execute()
