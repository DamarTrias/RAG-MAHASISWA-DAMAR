# Antarmuka formulir Masuk (Login) dan Daftar Akun (Register) Mahasiswa.
import streamlit as st
from core.auth import login_user, register_user


def render() -> None:
    # Merender form autentikasi di tengah layar.
    # Membuat tata letak kartu di tengah layar (centered card)
    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <div style="font-size: 48px; margin-bottom: 8px;">🎓</div>
            <h2 style="margin: 0; font-weight: 800;">Portal Belajar RAG Mahasiswa</h2>
            <p style="color: #94a3b8; font-size: 14px; margin-top: 4px;">
                Masuk atau buat akun untuk mengakses dokumen, obrolan, kuis, dan flashcard Anda secara terisolasi.
            </p>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["🔑 Masuk (Login)", "📝 Daftar Akun (Register)"])

        # ==========================================
        # TAB 1: FORMULIR MASUK (LOGIN)
        # ==========================================
        with tab_login:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            with st.form("form_login"):
                login_nim = st.text_input(
                    "Nomor Induk Mahasiswa (NIM):",
                    placeholder="Contoh: 21001",
                    key="input_login_nim"
                )
                login_password = st.text_input(
                    "Kata Sandi:",
                    type="password",
                    placeholder="Masukkan kata sandi Anda",
                    key="input_login_pass"
                )
                btn_login = st.form_submit_button(
                    "🚀 Masuk ke Akun",
                    type="primary",
                    use_container_width=True
                )

            if btn_login:
                with st.spinner("Memverifikasi kredensial..."):
                    success, user_data, msg = login_user(login_nim, login_password)
                    if success:
                        st.session_state["user"] = user_data
                        st.success("✅ Login berhasil! Mengalihkan ke dashboard...")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        # ==========================================
        # TAB 2: FORMULIR DAFTAR (REGISTER)
        # ==========================================
        with tab_register:
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            with st.form("form_register"):
                reg_name = st.text_input(
                    "Nama Lengkap Mahasiswa:",
                    placeholder="Contoh: Damar Trias Saputra",
                    key="input_reg_name"
                )
                reg_nim = st.text_input(
                    "NIM Mahasiswa:",
                    placeholder="Contoh: 21001",
                    key="input_reg_nim"
                )
                reg_password = st.text_input(
                    "Kata Sandi Baru (Min. 6 Karakter):",
                    type="password",
                    placeholder="Buat kata sandi yang aman",
                    key="input_reg_pass"
                )
                reg_confirm = st.text_input(
                    "Ulangi Kata Sandi:",
                    type="password",
                    placeholder="Ketik ulang kata sandi",
                    key="input_reg_confirm"
                )
                btn_register = st.form_submit_button(
                    "✨ Buat Akun Mahasiswa",
                    type="primary",
                    use_container_width=True
                )

            if btn_register:
                if reg_password != reg_confirm:
                    st.error("❌ Konfirmasi kata sandi tidak cocok. Silakan periksa kembali.")
                else:
                    with st.spinner("Mendaftarkan akun..."):
                        success, msg = register_user(reg_name, reg_nim, reg_password)
                        if success:
                            st.success(f"🎉 {msg}")
                        else:
                            st.error(f"❌ {msg}")
