"""
views/analisis_critic_topsis.py — Halaman 6: Analisis CRITIC-TOPSIS (Pastel Blue Minimalist)
"""
import streamlit as st
from critic_topsis import run_analysis, validate_data, build_decision_matrix, MONTH_NAMES
from database import save_analysis_result, get_all_categories
from ui_helpers import render_page_header, section_title


def _month_opts():
    return list(MONTH_NAMES.values())


def _month_num(label: str) -> int:
    return next(k for k, v in MONTH_NAMES.items() if v == label)


def show():
    render_page_header("Analisis CRITIC-TOPSIS", "Hitung bobot objektif kriteria dan peringkat prioritas pengadaan", icon_key="calc", tone="lavender")

    col_left, col_right = st.columns([3.3, 2], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown(
                '<div style="font-weight:600;color:#243B53;font-size:0.95rem;margin-bottom:0.65rem;">'
                'Periode Analisis</div>',
                unsafe_allow_html=True,
            )

            c1, c2, c3 = st.columns([0.9, 1.15, 1.15])
            with c1:
                tahun = st.selectbox("Tahun", [2024, 2025, 2026], index=2)
            with c2:
                bulan_awal_lbl = st.selectbox("Bulan Awal", _month_opts(), index=0)
            with c3:
                bulan_akhir_lbl = st.selectbox("Bulan Akhir", _month_opts(), index=10)

            bulan_awal = _month_num(bulan_awal_lbl)
            bulan_akhir = _month_num(bulan_akhir_lbl)

            if bulan_awal > bulan_akhir:
                st.error("Bulan Awal tidak boleh lebih besar dari Bulan Akhir.")
                return

            cats = get_all_categories()
            n_aktif = sum(1 for c in cats if c["status"] == "Aktif")

            st.markdown(f"""
            <div style="display:flex;flex-wrap:wrap;gap:0.75rem;margin-top:0.75rem;padding-top:0.75rem;
                        border-top:1px solid #F0F4F8;">
                <div style="text-align:center;flex:1 1 130px;background:#E6F0FA;border-radius:10px;padding:0.65rem;">
                    <div style="font-size:1.45rem;font-weight:700;color:#3A6BA5;">{n_aktif}</div>
                    <div style="font-size:0.76rem;color:#627D98;">Jumlah Alternatif</div>
                </div>
                <div style="text-align:center;flex:1 1 130px;background:#E6F6EE;border-radius:10px;padding:0.65rem;">
                    <div style="font-size:1.45rem;font-weight:700;color:#2D6A4F;">4</div>
                    <div style="font-size:0.76rem;color:#627D98;">Jumlah Kriteria</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        b1, b2, b3 = st.columns([1.15, 1, 1.2], gap="small")
        btn_preview = b1.button("Pratinjau Matriks", use_container_width=True)
        btn_validate = b2.button("Validasi Data", use_container_width=True)
        btn_run = b3.button("Jalankan Analisis", use_container_width=True, type="primary")

    with col_right:
        st.markdown("""
        <div style="background:#E6F0FA;border:1px solid #C8DDF3;border-radius:12px;
                    padding:1.25rem 1.5rem;height:100%;">
            <div style="font-weight:600;color:#1E4976;font-size:0.95rem;margin-bottom:0.65rem;">
                Informasi Metode
            </div>
            <p style="font-size:0.82rem;color:#486581;line-height:1.7;margin:0;">
                Pastikan data periode tersedia dan sudah divalidasi sebelum menjalankan analisis.
            </p>
            <div style="font-weight:600;font-size:0.82rem;color:#243B53;margin-top:0.85rem;margin-bottom:0.35rem;">
                Kriteria yang digunakan:
            </div>
            <ul style="font-size:0.81rem;color:#486581;line-height:1.85;margin:0;padding-left:1.15rem;">
                <li><b>C1 – Total Qty</b> (Benefit)</li>
                <li><b>C2 – Total Amount</b> (Benefit)</li>
                <li><b>C3 – Bulan Aktif</b> (Benefit)</li>
                <li><b>C4 – CV Qty</b> (Cost / Stabilitas)</li>
            </ul>
            <p style="font-size:0.8rem;color:#627D98;margin-top:0.85rem;margin-bottom:0;">
                Bobot dihitung secara objektif menggunakan metode <b>CRITIC</b>, lalu peringkat ditentukan dengan <b>TOPSIS</b>.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    # ── Pratinjau Matriks ─────────────────────────────────────────────────────
    if btn_preview:
        df = build_decision_matrix(tahun, bulan_awal, bulan_akhir)
        if df.empty:
            st.warning("Belum ada data untuk periode ini.")
        else:
            st.markdown("""
            <div class="soft-card">
                <div style="font-weight:600;color:#243B53;margin-bottom:0.75rem;">
                    Pratinjau Matriks Keputusan Awal
                </div>
            """, unsafe_allow_html=True)
            disp = df.rename(columns={
                "nama": "Kategori", "C1": "C1: Qty",
                "C2": "C2: Amount (Rp)", "C3": "C3: Bulan Aktif",
                "C4": "C4: CV Qty",
            })
            st.dataframe(
                disp[["Kategori", "C1: Qty", "C2: Amount (Rp)", "C3: Bulan Aktif", "C4: CV Qty"]],
                use_container_width=True, hide_index=True,
                column_config={
                    "C1: Qty": st.column_config.NumberColumn(format="%,.0f"),
                    "C2: Amount (Rp)": st.column_config.NumberColumn(format="Rp %,.0f"),
                    "C4: CV Qty": st.column_config.NumberColumn(format="%.4f"),
                },
            )
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Validasi Data ─────────────────────────────────────────────────────────
    if btn_validate:
        result = validate_data(tahun, bulan_awal, bulan_akhir)
        st.markdown("""
        <div class="soft-card">
            <div style="font-weight:600;color:#243B53;margin-bottom:0.75rem;">
                Hasil Validasi
            </div>
        """, unsafe_allow_html=True)

        for msg in result["messages"]:
            clean_msg = msg.replace("✅ ", "").replace("⚠ ", "").replace("ℹ ", "")
            if "✅" in msg:
                st.success(clean_msg)
            elif "⚠" in msg:
                st.warning(clean_msg)
            else:
                st.info(clean_msg)

        s = result["stats"]
        if s:
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Jumlah Alternatif", s.get("jumlah_alternatif", 0))
            with col_b:
                st.metric("Jumlah Kriteria", s.get("jumlah_kriteria", 4))

        st.markdown("</div>", unsafe_allow_html=True)

    # ── Jalankan Analisis ─────────────────────────────────────────────────────
    if btn_run:
        with st.spinner("Menghitung CRITIC dan TOPSIS..."):
            analysis = run_analysis(tahun, bulan_awal, bulan_akhir)

        if "error" in analysis:
            st.error(analysis["error"])
            return

        analysis["created_by"] = st.session_state.user["username"]
        analysis_id = save_analysis_result(analysis)
        analysis["analysis_id"] = analysis_id

        st.session_state.current_analysis = analysis
        st.session_state.current_analysis_id = analysis_id

        st.success(f"Analisis **{analysis_id}** selesai. {len(analysis['rankings'])} kategori telah diperingkat.")

        st.markdown(f"""
        <div class="soft-card" style="margin-top:0.75rem;">
            <div style="font-weight:600;color:#243B53;margin-bottom:0.75rem;">
                Hasil Peringkat — {analysis_id}
            </div>
        """, unsafe_allow_html=True)

        rank_colors = ["#6B9BD2", "#7BC4A4", "#E6A97E", "#A692D4", "#DF8C8A"]
        for r in analysis["rankings"]:
            rc = rank_colors[min(r["rank"] - 1, len(rank_colors) - 1)]
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.75rem;
                        padding:0.55rem 0;border-bottom:1px solid #F0F4F8;">
                <div style="width:26px;height:26px;border-radius:50%;background:{rc};
                            color:white;font-weight:700;font-size:0.78rem;
                            display:flex;align-items:center;justify-content:center;
                            flex-shrink:0;">{r['rank']}</div>
                <div style="flex:1;font-weight:500;font-size:0.86rem;color:#243B53;">{r['nama']}</div>
                <div style="font-weight:700;color:#3A6BA5;font-size:0.88rem;">
                    {r['nilai_preferensi']:.4f}
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.info("Buka menu **Hasil Analisis** untuk melihat grafik dan detail lengkap.")
