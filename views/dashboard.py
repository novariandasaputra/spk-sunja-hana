"""
views/dashboard.py — Halaman Dashboard (Pastel Blue Minimalist)
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from database import get_dashboard_stats, get_monthly_sales, get_latest_analysis
from ui_helpers import render_page_header, render_kpi_grid, section_title, pill_badge

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
               "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]


def show():
    render_page_header("Dashboard", "Ringkasan data penjualan dan prioritas pengadaan produk", icon_key="dashboard", tone="blue")

    # ── KPI Cards (Responsive Grid) ───────────────────────────────────────────
    stats = get_dashboard_stats()
    render_kpi_grid([
        {"icon_key": "folder",   "value": stats["total_categories"],              "label": "Kategori Produk",   "accent": "#5B9BD5", "bg": "#E6F1FC", "text_color": "#3A72B0"},
        {"icon_key": "calendar", "value": stats["total_months"],                  "label": "Bulan Data",        "accent": "#52B788", "bg": "#E3F6EC", "text_color": "#246A49"},
        {"icon_key": "chart",    "value": stats["total_analysis"],                "label": "Total Analisis",    "accent": "#F4A261", "bg": "#FEF0E3", "text_color": "#A0521D"},
        {"icon_key": "clock",    "value": stats["last_analysis"].split(",")[0],   "label": "Analisis Terakhir", "accent": "#9D84D8", "bg": "#EFEAFA", "text_color": "#553C9A"},
    ])

    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)

    # ── Main Content: Chart (left) + Priority List (right) ────────────────────
    col_chart, col_priority = st.columns([1.35, 1], gap="medium")

    with col_chart:
        _render_sales_chart()

    with col_priority:
        _render_priority_list()

    st.markdown("<div style='margin-top:1.25rem;'></div>", unsafe_allow_html=True)

    # ── Informasi Sistem ──────────────────────────────────────────────────────
    _render_system_info(stats)


# ── Helper: Sales Trend Chart ─────────────────────────────────────────────────
def _render_sales_chart():
    with st.container(border=True):
        section_title("Tren Penjualan Kategori", icon_key="trend", tone="blue")

        sales = get_monthly_sales(2026)
        if not sales:
            st.info("Belum ada data penjualan.")
            return

        df = pd.DataFrame(sales)
        pivot = df.pivot_table(index="bulan", columns="nama", values="qty", aggfunc="sum").reset_index()
        pivot["bulan_label"] = pivot["bulan"].apply(lambda x: MONTH_NAMES[x - 1])

        # Pastel chart palette
        colors = ["#6B9BD2", "#7BC4A4", "#E6A97E", "#A692D4", "#DF8C8A"]
        fig = go.Figure()

        kategori_cols = [c for c in pivot.columns if c not in ("bulan", "bulan_label")]
        for i, kat in enumerate(kategori_cols):
            fig.add_trace(go.Scatter(
                x=pivot["bulan_label"],
                y=pivot[kat],
                mode="lines+markers",
                name=kat,
                line=dict(color=colors[i % len(colors)], width=2.5),
                marker=dict(size=6),
            ))

        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#F9FBFD",
            font=dict(family="Inter, sans-serif", size=11, color="#486581"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0,
                font=dict(size=10),
            ),
            xaxis=dict(showgrid=False, tickfont=dict(size=10)),
            yaxis=dict(
                gridcolor="#EDF2F7",
                showgrid=True,
                tickformat=",",
                tickfont=dict(size=10),
            ),
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ── Helper: Priority List ─────────────────────────────────────────────────────
def _render_priority_list():
    latest = get_latest_analysis()
    rankings = latest.get("result_data", {}).get("rankings", []) if latest else []

    if rankings:
        priorities = []
        for r in rankings[:5]:
            if r["rank"] == 1:
                badge, tone = "Prioritas Utama", "mint"
            elif r["rank"] <= 3:
                badge, tone = "Prioritas Tinggi", "blue"
            else:
                badge, tone = "Prioritas Menengah", "peach"
            priorities.append({
                "rank": r["rank"],
                "nama": r["nama"].upper(),
                "nilai": r["nilai_preferensi"],
                "badge": badge,
                "tone": tone,
            })
    else:
        priorities = [
            {"rank": 1, "nama": "ROKOK",          "nilai": 0.9743, "badge": "Prioritas Utama",    "tone": "mint"},
            {"rank": 2, "nama": "ALAT TULIS",     "nilai": 0.3365, "badge": "Prioritas Tinggi",   "tone": "blue"},
            {"rank": 3, "nama": "MINUMAN INSTAN", "nilai": 0.3229, "badge": "Prioritas Tinggi",   "tone": "blue"},
            {"rank": 4, "nama": "SNACK",          "nilai": 0.3060, "badge": "Prioritas Menengah", "tone": "peach"},
            {"rank": 5, "nama": "ANEKA SUSU",     "nilai": 0.2977, "badge": "Prioritas Menengah", "tone": "peach"},
        ]

    rank_colors = ["#6B9BD2", "#7BC4A4", "#E6A97E", "#A692D4", "#DF8C8A"]

    with st.container(border=True):
        section_title("5 Prioritas Kategori", icon_key="award", tone="mint")

        rows_html = []
        for idx, p in enumerate(priorities):
            rc = rank_colors[(p["rank"] - 1) % len(rank_colors)]
            badge_html = pill_badge(p["badge"], p["tone"])
            border_b = "border-bottom:1px solid #F0F4F8;" if idx < len(priorities) - 1 else ""
            rows_html.append(f"""
            <div style="display:flex; align-items:center; gap:0.75rem;
                        padding:0.65rem 0; {border_b}">
                <div style="
                    width:26px; height:26px; border-radius:50%;
                    background:{rc}; color:white;
                    font-weight:700; font-size:0.78rem;
                    display:flex; align-items:center; justify-content:center;
                    flex-shrink:0;
                ">{p['rank']}</div>
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:600; font-size:0.82rem; color:#243B53;
                                white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                        {p['nama']}
                    </div>
                    <div style="font-size:0.72rem; color:#627D98;">
                        Nilai Preferensi: {p['nilai']:.4f}
                    </div>
                </div>
                {badge_html}
            </div>
            """)
        st.markdown("".join(rows_html), unsafe_allow_html=True)


# ── Helper: System Info ───────────────────────────────────────────────────────
def _render_system_info(stats):
    with st.container(border=True):
        section_title("Informasi Sistem", icon_key="info", tone="lavender")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="font-size:0.83rem; line-height:2.1; color:#486581;">
                <span style="color:#6B9BD2;">•</span>
                <b>Periode Data</b> : Jan – Nov 2026<br>
                <span style="color:#6B9BD2;">•</span>
                <b>Jumlah Kategori Aktif</b> : {stats['total_categories']}<br>
                <span style="color:#6B9BD2;">•</span>
                <b>Kategori dengan Data</b> : {stats['total_categories']}
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="font-size:0.83rem; line-height:2.1; color:#486581;">
                <span style="color:#6B9BD2;">•</span>
                <b>Analisis Terakhir</b> : {stats['last_analysis']}<br>
                <span style="color:#6B9BD2;">•</span>
                <b>Total Analisis</b> : {stats['total_analysis']}<br>
                <span style="color:#7BC4A4;">•</span>
                <b>Status Database</b> : {pill_badge("Terhubung", "mint")}
            </div>
            """, unsafe_allow_html=True)
