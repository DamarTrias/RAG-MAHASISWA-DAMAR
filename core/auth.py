"""Modul autentikasi mahasiswa: Hashing kata sandi, Registrasi, dan Login."""
import hashlib
import hmac
import secrets
from typing import Tuple, Optional, Dict, Any
from core.db import db


def hash_password(password: str) -> str:
    """Mengamankan kata sandi dengan salt kriptografis unik 16-byte menggunakan PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000
    )
    return f"{salt}${key.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Memeriksa kecocokan kata sandi dengan hash yang tersimpan secara aman dari timing attack."""
    if not stored_hash or "$" not in stored_hash:
        return False
    try:
        salt, expected_key = stored_hash.split("$", 1)
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000
        )
        return hmac.compare_digest(key.hex(), expected_key)
    except Exception:
        return False


def register_user(name: str, nim: str, password: str) -> Tuple[bool, str]:
    """Mendaftarkan akun mahasiswa baru ke tabel students di Supabase."""
    name_clean = name.strip()
    nim_clean = nim.strip()
    pass_clean = password.strip()

    # Validasi input
    if len(name_clean) < 3:
        return False, "Nama lengkap minimal 3 karakter."
    if not nim_clean:
        return False, "NIM wajib diisi."
    if len(pass_clean) < 6:
        return False, "Kata sandi minimal 6 karakter."

    try:
        # Cek apakah NIM sudah terdaftar sebelumnya
        existing = db.table("students").select("id").eq("nim", nim_clean).execute()
        if existing.data:
            return False, f"NIM '{nim_clean}' sudah terdaftar. Silakan gunakan NIM lain atau login."

        # Simpan mahasiswa baru dengan password yang sudah di-hash
        pass_hash = hash_password(pass_clean)
        insert_res = db.table("students").insert({
            "name": name_clean,
            "nim": nim_clean,
            "password_hash": pass_hash
        }).execute()

        if insert_res.data:
            return True, "Pendaftaran berhasil! Silakan masuk menggunakan akun baru Anda."
        return False, "Gagal menyimpan akun ke basis data."
    except Exception as e:
        return False, f"Terjadi kesalahan saat pendaftaran: {e}"


def login_user(nim: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """Memverifikasi kredensial NIM dan kata sandi mahasiswa."""
    nim_clean = nim.strip()
    pass_clean = password.strip()

    if not nim_clean or not pass_clean:
        return False, None, "NIM dan kata sandi wajib diisi."

    try:
        res = db.table("students").select("*").eq("nim", nim_clean).execute()
        if not res.data:
            return False, None, "NIM tidak ditemukan. Pastikan NIM sudah benar atau daftar akun baru."

        student = res.data[0]
        stored_hash = student.get("password_hash")

        # Jika akun lama belum memiliki password_hash
        if not stored_hash:
            return False, None, "Akun ini belum memiliki kata sandi. Silakan daftarkan ulang akun Anda."

        if verify_password(pass_clean, stored_hash):
            return True, student, "Login berhasil!"
        else:
            return False, None, "Kata sandi salah. Silakan periksa kembali."
    except Exception as e:
        return False, None, f"Terjadi kesalahan saat verifikasi: {e}"
