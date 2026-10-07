"""Tampilan tab Generatif Soal (Kuis Pilihan Ganda & Essay)."""
from typing import Dict, Any
import streamlit as st
from core.generator import make_quiz
from ui.common import pick_document


def render(student: Dict[str, Any]) -> None:
    """Merender tab generator soal latihan ujian otomatis dari materi."""
    kiri, kanan = st.columns([1, 2])
    quiz_key = f"quiz_{student['id']}"

    with kiri:
        st.subheader("Konfigurasi Pembuat Soal")
        doc_id = pick_document(student["id"], label="Pilih Dokumen Sumber:", key=f"quiz_doc_{student['id']}")
        jumlah = st.selectbox("Jumlah Soal:", [3, 5, 10], index=1, key=f"quiz_qty_{student['id']}")
        level = st.selectbox("Tingkat Kesulitan:", ["Mudah", "Sedang", "Sulit"], index=1, key=f"quiz_lvl_{student['id']}")
        tipe = st.selectbox("Tipe Soal:", ["Pilihan Ganda", "Essay"], key=f"quiz_type_{student['id']}")
        
        if st.button("✨ Buat Soal dari Dokumen", type="primary", use_container_width=True, key=f"quiz_btn_{student['id']}"):
            with st.spinner("Menganalisis materi & menyusun soal kuis cerdas..."):
                try:
                    st.session_state[quiz_key] = {
                        "soal_list": make_quiz(student["id"], doc_id, jumlah, level, tipe),
                        "tipe": tipe,
                        "submitted": False,
                        "user_answers": {}
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal membuat soal: {e}")

    with kanan:
        st.subheader("Latihan Soal Ujian")
        quiz_data = st.session_state.get(quiz_key)
        
        if not quiz_data or not quiz_data.get("soal_list"):
            st.info("Pilih konfigurasi di sebelah kiri dan klik 'Buat Soal dari Dokumen' untuk menghasilkan kuis.")
            return

        soal_list = quiz_data["soal_list"]
        is_pg = (quiz_data["tipe"] == "Pilihan Ganda")

        with st.form(f"quiz_form_{student['id']}"):
            answers = {}
            for i, s in enumerate(soal_list, 1):
                st.markdown(f"**{i}. {s.pertanyaan}**")
                
                if is_pg and s.pilihan:
                    ans = st.radio(
                        f"Pilihan {i}",
                        options=s.pilihan,
                        index=None,
                        key=f"q_choice_{student['id']}_{i}",
                        label_visibility="collapsed"
                    )
                    answers[i] = ans
                else:
                    ans = st.text_area(
                        "Jawaban Anda:",
                        key=f"q_essay_{student['id']}_{i}",
                        placeholder="Tuliskan analisis atau jawaban Anda di sini..."
                    )
                    answers[i] = ans

                st.markdown("<hr style='margin: 12px 0; border: 0; border-top: 1px solid rgba(255,255,255,0.06);'>", unsafe_allow_html=True)

            submit_btn = st.form_submit_button("✅ Kumpulkan & Periksa Jawaban", type="primary")
            if submit_btn:
                quiz_data["submitted"] = True
                quiz_data["user_answers"] = answers
                st.rerun()

        # Tampilkan Pembahasan & Nilai jika sudah dikumpulkan
        if quiz_data.get("submitted"):
            st.markdown("### 📊 Hasil & Pembahasan")
            correct_count = 0
            
            for i, s in enumerate(soal_list, 1):
                usr_ans = quiz_data["user_answers"].get(i, "")
                
                if is_pg:
                    # Validasi apakah jawaban pengguna cocok dengan huruf kunci (A, B, C, D)
                    is_correct = bool(usr_ans and usr_ans.strip().startswith(s.jawaban.strip()))
                    if is_correct:
                        correct_count += 1
                        st.success(f"**Nomor {i}: Benar! 🎉** (Jawaban Anda: {usr_ans})")
                    else:
                        st.error(f"**Nomor {i}: Salah.** Jawaban Anda: {usr_ans or 'Kosong'} | Kunci: **{s.jawaban}**")
                else:
                    st.markdown(f"**Soal {i}:**")
                    st.caption(f"Jawaban Anda: {usr_ans or 'Kosong'}")
                    st.info(f"💡 **Model Jawaban Ideal:** {s.jawaban}")

                with st.expander(f"Lihat Pembahasan Lengkap No. {i}"):
                    st.write(s.pembahasan)
                    st.caption(f"📚 Rujukan: {s.sumber}")

            if is_pg:
                score = int((correct_count / len(soal_list)) * 100)
                st.metric(label="Skor Kuis Anda", value=f"{score} / 100")
