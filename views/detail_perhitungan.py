"""
views/detail_perhitungan.py — Halaman 8: Detail Perhitungan (Pastel Blue Minimalist)
"""
import streamlit as st
import pandas as pd
from database import get_latest_analysis
from ui_helpers import render_page_header


def _pastel_highlight(series, base_rgb=(210, 232, 250)):
    """Pure-Python pastel cell background gradient (no matplotlib required)."""
    vals = series.astype(float)
    vmin, vmax = vals.min(), vals.max()
    span = vmax - vmin
    styles = []
    for v in vals:
        t = (v - vmin) / span if span > 0 else 0.5
        alpha = 0.15 + 0.65 * t
        r, g, b = base_rgb
        styles.append(f"background-color: rgba({r}, {g}, {b}, {alpha:.2f}); color: #1E293B;")
    return styles


def _load_analysis() -> dict:
    if st.session_state.get("current_analysis"):
        return st.session_state.current_analysis
    rec = get_latest_analysis()
    return rec.get("result_data", {}) if rec else {}


def show():
    aid = st.session_state.get(
        "current_analysis_id",
        st.session_state.get("current_analysis", {}).get("analysis_id", "—"),
    )
    render_page_header(f"Detail Perhitungan ({aid})", "Rincian tahapan perhitungan metode CRITIC dan TOPSIS", icon_key="layers", tone="lavender")

    result = _load_analysis()
    if not result or "decision_matrix" not in result:
        st.info("Belum ada hasil analisis. Jalankan analisis melalui menu **Analisis CRITIC-TOPSIS**.")
        return

    dm = result["decision_matrix"]
    critic = result["critic"]
    topsis = result["topsis"]
    rankings = result["rankings"]
    alts = dm["index"]
    cols_l = dm["labels"]

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Matriks Awal",
        "Bobot CRITIC",
        "Normalisasi TOPSIS",
        "Solusi Ideal",
        "Nilai Preferensi",
    ])

    # ── Tab 1: Matriks Awal ───────────────────────────────────────────────────
    with tab1:
        st.markdown(
            '<p style="color:#627D98;font-size:0.83rem;margin-bottom:0.75rem;">'
            'Matriks Keputusan Awal <b>X</b> berisi nilai asli dari setiap alternatif pada keempat kriteria.</p>',
            unsafe_allow_html=True,
        )

        df_raw = pd.DataFrame(dm["data"], index=alts, columns=cols_l)
        st.dataframe(
            df_raw.style.format({
                cols_l[0]: "{:,.0f}",
                cols_l[1]: "Rp {:,.0f}",
                cols_l[2]: "{:.0f}",
                cols_l[3]: "{:.4f}",
            }),
            use_container_width=True,
        )

        types = dm.get("types", [])
        if types:
            type_rows = [{
                "Kriteria": lbl,
                "Tipe": "Benefit (lebih tinggi lebih baik)" if t == "benefit" else "Cost (lebih rendah lebih baik)",
            } for lbl, t in zip(cols_l, types)]
            st.dataframe(pd.DataFrame(type_rows), use_container_width=True, hide_index=True)

    # ── Tab 2: Bobot CRITIC ───────────────────────────────────────────────────
    with tab2:
        st.markdown(
            '<p style="color:#627D98;font-size:0.83rem;margin-bottom:0.75rem;">'
            'Bobot <b>CRITIC</b> dihitung berdasarkan standar deviasi dan korelasi antar kriteria.</p>',
            unsafe_allow_html=True,
        )

        st.markdown("**1. Matriks Ternormalisasi (Min-Max)**")
        df_norm = pd.DataFrame(critic["normalized"], index=alts, columns=cols_l)
        st.dataframe(df_norm.style.format("{:.6f}"), use_container_width=True)

        st.markdown("**2. Statistik Bobot CRITIC**")
        stat_df = pd.DataFrame({
            "Kriteria":         cols_l,
            "Std Dev (σ)":      critic["std_dev"],
            "Conflict Σ(1-r)":  critic["conflict"],
            "Information (Cj)": critic["information"],
            "Bobot (wj)":       critic["weights"],
        })
        st.dataframe(
            stat_df.style.format({
                "Std Dev (σ)":      "{:.6f}",
                "Conflict Σ(1-r)":  "{:.6f}",
                "Information (Cj)": "{:.6f}",
                "Bobot (wj)":       "{:.6f}",
            }),
            use_container_width=True, hide_index=True,
        )

        st.markdown("**3. Matriks Korelasi Antar Kriteria**")
        df_corr = pd.DataFrame(critic["correlation"], index=cols_l, columns=cols_l)
        st.dataframe(
            df_corr.style.format("{:.4f}").apply(_pastel_highlight, axis=0),
            use_container_width=True,
        )

    # ── Tab 3: Normalisasi TOPSIS ─────────────────────────────────────────────
    with tab3:
        st.markdown(
            '<p style="color:#627D98;font-size:0.83rem;margin-bottom:0.75rem;">'
            'Normalisasi vektor <code>r_ij = x_ij / √Σ x_ij²</code> dan matriks terbobot <code>v_ij = w_j · r_ij</code>.</p>',
            unsafe_allow_html=True,
        )

        st.markdown("**1. Matriks Ternormalisasi (R)**")
        df_r = pd.DataFrame(topsis["r_matrix"], index=alts, columns=cols_l)
        st.dataframe(df_r.style.format("{:.6f}"), use_container_width=True)

        st.markdown("**2. Matriks Terbobot (V)**")
        df_v = pd.DataFrame(topsis["v_matrix"], index=alts, columns=cols_l)
        st.dataframe(df_v.style.format("{:.6f}"), use_container_width=True)

    # ── Tab 4: Solusi Ideal ───────────────────────────────────────────────────
    with tab4:
        st.markdown(
            '<p style="color:#627D98;font-size:0.83rem;margin-bottom:0.75rem;">'
            'Solusi ideal positif <b>A⁺</b> dan solusi ideal negatif <b>A⁻</b> beserta jarak Euclidean.</p>',
            unsafe_allow_html=True,
        )

        ideal_df = pd.DataFrame({
            "Kriteria": cols_l,
            "Tipe":     dm.get("types", ["benefit"] * 4),
            "A⁺ (PIS)": topsis["pis"],
            "A⁻ (NIS)": topsis["nis"],
        })
        st.dataframe(
            ideal_df.style.format({"A⁺ (PIS)": "{:.6f}", "A⁻ (NIS)": "{:.6f}"}),
            use_container_width=True, hide_index=True,
        )

        st.markdown("**Jarak Alternatif ke Solusi Ideal**")
        dist_df = pd.DataFrame({
            "Alternatif":  alts,
            "D⁺ (ke PIS)": topsis["d_plus"],
            "D⁻ (ke NIS)": topsis["d_minus"],
        })
        st.dataframe(
            dist_df.style.format({"D⁺ (ke PIS)": "{:.6f}", "D⁻ (ke NIS)": "{:.6f}"}),
            use_container_width=True, hide_index=True,
        )

    # ── Tab 5: Nilai Preferensi ───────────────────────────────────────────────
    with tab5:
        st.markdown(
            '<p style="color:#627D98;font-size:0.83rem;margin-bottom:0.75rem;">'
            'Nilai preferensi <code>V_i = D⁻ / (D⁺ + D⁻)</code>. Semakin tinggi V_i, semakin tinggi prioritas pengadaan.</p>',
            unsafe_allow_html=True,
        )

        pref_rows = [{
            "Peringkat":             r["rank"],
            "Kategori":              r["nama"],
            "D⁺":                    r["d_plus"],
            "D⁻":                    r["d_minus"],
            "Nilai Preferensi (Vi)": r["nilai_preferensi"],
        } for r in rankings]

        pref_df = pd.DataFrame(pref_rows)
        st.dataframe(
            pref_df.style
                .format({"D⁺": "{:.6f}", "D⁻": "{:.6f}", "Nilai Preferensi (Vi)": "{:.4f}"})
                .apply(_pastel_highlight, subset=["Nilai Preferensi (Vi)"], base_rgb=(183, 228, 199)),
            use_container_width=True, hide_index=True,
        )

        st.markdown("""
        <div style="margin-top:0.75rem;padding:0.85rem 1rem;background:#E6F0FA;border:1px solid #C8DDF3;
                    border-radius:10px;font-size:0.82rem;color:#1E4976;">
            <b>Interpretasi:</b> Kategori dengan nilai preferensi tertinggi adalah kategori yang paling
            diprioritaskan untuk pengadaan berdasarkan keempat kriteria secara objektif.
        </div>
        """, unsafe_allow_html=True)
