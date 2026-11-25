"""
views/riwayat_analisis.py — Halaman 9: Riwayat Analisis (Pastel Blue Minimalist)
"""
import streamlit as st
import json
from database import get_analysis_history, get_analysis_by_id
from ui_helpers import render_page_header, pill_badge

ITEMS_PER_PAGE = 5


def show():
    render_page_header("Riwayat Analisis", "Daftar seluruh analisis CRITIC-TOPSIS yang telah dijalankan", icon_key="clock", tone="peach")

    history = get_analysis_history()
    if not history:
        st.info("Belum ada riwayat analisis. Jalankan analisis melalui menu **Analisis CRITIC-TOPSIS**.")
        return

    if "riwayat_page" not in st.session_state:
        st.session_state.riwayat_page = 0

    total_pages = max(1, (len(history) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
    page = st.session_state.riwayat_page
    page_items = history[page * ITEMS_PER_PAGE: (page + 1) * ITEMS_PER_PAGE]

    with st.container(border=True):
        h_cols = st.columns([0.4, 0.85, 1.45, 1.75, 0.7, 0.85, 0.95, 1.2], vertical_alignment="center")
        for col, h in zip(h_cols, ["No", "ID", "Tanggal", "Periode", "Alt.", "Kriteria", "Status", "Aksi"]):
            col.markdown(
                f'<div style="font-weight:600;font-size:0.78rem;color:#627D98;'
                f'text-transform:uppercase;letter-spacing:0.03em;padding:0.25rem 0;">{h}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="border-color:#E2ECF5;margin:0.35rem 0 0.5rem;">', unsafe_allow_html=True)

        for i, rec in enumerate(page_items):
            global_i = page * ITEMS_PER_PAGE + i
            periode = f"{rec.get('periode_awal', '?')} – {rec.get('periode_akhir', '?')}"
            if rec.get("result_json"):
                try:
                    rdata = json.loads(rec["result_json"])
                    if rdata.get("tahun"):
                        periode += f" {rdata['tahun']}"
                except Exception:
                    pass

            r_cols = st.columns([0.4, 0.85, 1.45, 1.75, 0.7, 0.85, 0.95, 1.2], vertical_alignment="center")
            r_cols[0].markdown(f'<span style="color:#627D98;font-size:0.85rem;">{global_i + 1}</span>', unsafe_allow_html=True)
            r_cols[1].markdown(
                f'<span style="font-family:monospace;color:#3A6BA5;background:#E6F0FA;'
                f'padding:0.15em 0.5em;border-radius:6px;font-size:0.8rem;font-weight:600;">{rec.get("analysis_id","—")}</span>',
                unsafe_allow_html=True,
            )
            r_cols[2].markdown(f'<span style="color:#486581;font-size:0.84rem;">{rec.get("tanggal","—")}</span>', unsafe_allow_html=True)
            r_cols[3].markdown(f'<span style="color:#243B53;font-size:0.84rem;font-weight:500;">{periode}</span>', unsafe_allow_html=True)
            r_cols[4].markdown(f'<span style="color:#486581;font-size:0.84rem;">{rec.get("jumlah_alternatif","—")}</span>', unsafe_allow_html=True)
            r_cols[5].markdown(f'<span style="color:#486581;font-size:0.84rem;">{rec.get("jumlah_kriteria","—")}</span>', unsafe_allow_html=True)

            badge = pill_badge("Selesai", "mint") if rec.get("status") == "Selesai" else pill_badge("Proses", "peach")
            r_cols[6].markdown(badge, unsafe_allow_html=True)

            with r_cols[7]:
                if st.button("Detail", key=f"view_{rec['analysis_id']}", use_container_width=True):
                    full_rec = get_analysis_by_id(rec["analysis_id"])
                    if full_rec and full_rec.get("result_data"):
                        rdata = full_rec["result_data"]
                        rdata["analysis_id"] = rec["analysis_id"]
                        st.session_state.current_analysis = rdata
                        st.session_state.current_analysis_id = rec["analysis_id"]
                        st.session_state.current_page = "Detail Perhitungan"
                        st.rerun()
                    else:
                        st.warning("Detail perhitungan tidak tersedia untuk riwayat dummy awal.")

            if i < len(page_items) - 1:
                st.markdown('<hr style="border-color:#F0F4F8;margin:0.35rem 0;">', unsafe_allow_html=True)

    # ── Pagination ────────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
    col_info, col_prev, col_pages, col_next = st.columns([4.5, 0.8, 1.5, 0.8], vertical_alignment="center")

    with col_info:
        st.markdown(
            f'<span style="font-size:0.8rem;color:#627D98;">'
            f'Menampilkan {page * ITEMS_PER_PAGE + 1}–'
            f'{min((page + 1) * ITEMS_PER_PAGE, len(history))} '
            f'dari {len(history)} riwayat</span>',
            unsafe_allow_html=True,
        )
    with col_prev:
        if st.button("Prev", disabled=(page == 0), use_container_width=True):
            st.session_state.riwayat_page -= 1
            st.rerun()
    with col_pages:
        st.markdown(
            f'<div style="text-align:center;font-size:0.82rem;color:#486581;">'
            f'Hal {page + 1} / {total_pages}</div>',
            unsafe_allow_html=True,
        )
    with col_next:
        if st.button("Next", disabled=(page >= total_pages - 1), use_container_width=True):
            st.session_state.riwayat_page += 1
            st.rerun()
