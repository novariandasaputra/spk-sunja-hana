"""
views/hasil_analisis.py — Halaman 7: Hasil Analisis (Pastel Blue Minimalist)
"""
import streamlit as st
import plotly.graph_objects as go
from database import get_latest_analysis
from ui_helpers import render_page_header, section_title, pill_badge


def _load_analysis() -> dict:
    if st.session_state.get("current_analysis"):
        return st.session_state.current_analysis
    rec = get_latest_analysis()
    if rec and rec.get("result_data"):
        return rec["result_data"]
    return {}


def show():
    render_page_header("Hasil Analisis", "Visualisasi nilai preferensi dan urutan prioritas kategori", icon_key="trend", tone="mint")

    result = _load_analysis()
    if not result or "rankings" not in result:
        st.info("Belum ada hasil analisis. Jalankan analisis terlebih dahulu melalui menu **Analisis CRITIC-TOPSIS**.")
        return

    aid = result.get("analysis_id", st.session_state.get("current_analysis_id", "—"))
    period = result.get("periode_label", "—")

    # ── Meta & Action Buttons ─────────────────────────────────────────────────
    col_meta, col_b1, col_b2 = st.columns([4.5, 1.5, 1.5], vertical_alignment="center")
    with col_meta:
        st.markdown(f"""
        <div style="display:flex;gap:0.75rem;align-items:center;flex-wrap:wrap;font-size:0.83rem;color:#627D98;">
            {pill_badge(f"ID: {aid}", "blue")}
            <span>Periode: <b style="color:#243B53;">{period}</b></span>
            <span>•</span>
            <span>{result.get('jumlah_alternatif', 0)} Alternatif &nbsp;|&nbsp; {result.get('jumlah_kriteria', 4)} Kriteria</span>
        </div>
        """, unsafe_allow_html=True)
    with col_b1:
        if st.button("Detail Perhitungan", use_container_width=True):
            st.session_state.current_page = "Detail Perhitungan"
            st.rerun()
    with col_b2:
        if st.button("Unduh Laporan", type="primary", use_container_width=True):
            st.session_state.current_page = "Laporan"
            st.rerun()

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

    rankings = result["rankings"]
    col_chart, col_rank = st.columns([3, 2], gap="large")

    # ── Bar Chart ─────────────────────────────────────────────────────────────
    with col_chart:
        with st.container(border=True):
            section_title("Grafik Nilai Preferensi TOPSIS", icon_key="chart", tone="blue")

            sorted_r = sorted(rankings, key=lambda x: x["nilai_preferensi"])
            names = [r["nama"] for r in sorted_r]
            values = [r["nilai_preferensi"] for r in sorted_r]
            pastel_bars = ["#E57373", "#9D84D8", "#F4A261", "#52B788", "#5B9BD5"]
            colors = pastel_bars[-len(sorted_r):]

            fig = go.Figure(go.Bar(
                y=names,
                x=values,
                orientation="h",
                marker=dict(color=colors, line=dict(width=0)),
                text=[f"{v:.4f}" for v in values],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Nilai Preferensi: %{x:.4f}<extra></extra>",
            ))
            fig.update_layout(
                margin=dict(l=0, r=50, t=10, b=10),
                height=300,
                xaxis=dict(range=[0, 1.12], gridcolor="#EDF2F7", title="Nilai Preferensi (Vi)", tickformat=".2f"),
                yaxis=dict(showgrid=False),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="#F9FBFD",
                font=dict(family="Segoe UI, sans-serif", size=11, color="#475569"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── Ranking Table ─────────────────────────────────────────────────────────
    with col_rank:
        with st.container(border=True):
            section_title("Tabel Peringkat", icon_key="award", tone="mint")

            rank_colors = ["#5B9BD5", "#52B788", "#F4A261", "#9D84D8", "#E57373"]
            priority_map = {
                1: ("Prioritas Utama", "mint"),
                2: ("Prioritas Tinggi", "blue"),
                3: ("Prioritas Tinggi", "blue"),
            }

            rows_html = []
            for idx, r in enumerate(rankings):
                rc = rank_colors[min(r["rank"] - 1, len(rank_colors) - 1)]
                badge_label, tone = priority_map.get(r["rank"], ("Prioritas Menengah", "peach"))
                border_b = "border-bottom:1px solid #F0F4F8;" if idx < len(rankings) - 1 else ""
                rows_html.append(f"""
                <div style="display:flex;align-items:center;gap:0.75rem;
                            padding:0.65rem 0;{border_b}">
                    <div style="width:26px;height:26px;border-radius:50%;background:{rc};
                                color:white;font-weight:700;font-size:0.78rem;
                                display:flex;align-items:center;justify-content:center;
                                flex-shrink:0;">{r['rank']}</div>
                    <div style="flex:1;min-width:0;">
                        <div style="font-weight:600;font-size:0.83rem;color:#1E293B;">{r['nama']}</div>
                        <div style="font-size:0.72rem;color:#64748B;">Vi = {r['nilai_preferensi']:.4f}</div>
                    </div>
                    {pill_badge(badge_label, tone)}
                </div>
                """)
            st.markdown("".join(rows_html), unsafe_allow_html=True)

    # ── CRITIC Weights ────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    weights = result.get("critic", {}).get("weights", [])
    labels = result.get("decision_matrix", {}).get("labels", [])

    if weights and labels:
        with st.container(border=True):
            section_title("Bobot Kriteria (CRITIC)", icon_key="calc", tone="lavender")

            wc = st.columns(len(weights))
            card_styles = [
                ("#E6F1FC", "#3A72B0"),
                ("#E3F6EC", "#246A49"),
                ("#FEF0E3", "#A0521D"),
                ("#EFEAFA", "#553C9A"),
            ]
            for i, (col, w, lbl) in enumerate(zip(wc, weights, labels)):
                bg, fg = card_styles[i % len(card_styles)]
                with col:
                    st.markdown(f"""
                    <div style="text-align:center;padding:0.8rem;border-radius:10px;background:{bg};">
                        <div style="font-size:1.3rem;font-weight:700;color:{fg};">{w:.4f}</div>
                        <div style="font-size:0.74rem;color:#475569;margin-top:0.2rem;">{lbl}</div>
                    </div>
                    """, unsafe_allow_html=True)
