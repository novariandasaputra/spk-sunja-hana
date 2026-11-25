"""
views/data_penjualan.py — Halaman Data Penjualan Bulanan (Pastel Blue Minimalist)
"""
import streamlit as st
import pandas as pd
from database import get_connection
from ui_helpers import render_page_header, render_kpi_grid, section_title

MONTH_NAMES = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember",
}


def _get_sales(tahun: int, bulan: int) -> pd.DataFrame:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id as category_id, c.kode AS "Kode", c.nama AS "Kategori",
               COALESCE(ms.qty, 0)    AS "Qty",
               COALESCE(ms.amount, 0) AS "Amount (Rp)"
        FROM categories c
        LEFT JOIN monthly_sales ms
               ON ms.category_id = c.id
              AND ms.tahun = ?
              AND ms.bulan = ?
        WHERE c.status = 'Aktif'
        ORDER BY c.kode
    """, (tahun, bulan))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        return pd.DataFrame(columns=["category_id", "Kode", "Kategori", "Qty", "Amount (Rp)"])
    return pd.DataFrame([dict(r) for r in rows])


def _upsert_sales(tahun: int, bulan: int, df: pd.DataFrame):
    conn = get_connection()
    cur = conn.cursor()
    errors = []
    saved = 0
    for _, row in df.iterrows():
        cat_id = int(row["category_id"])
        qty = int(row["Qty"]) if pd.notna(row["Qty"]) else 0
        amount = float(row["Amount (Rp)"]) if pd.notna(row["Amount (Rp)"]) else 0.0
        try:
            cur.execute("""
                INSERT INTO monthly_sales (category_id, tahun, bulan, qty, amount)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(category_id, tahun, bulan)
                DO UPDATE SET qty=excluded.qty, amount=excluded.amount
            """, (cat_id, tahun, bulan, qty, amount))
            saved += 1
        except Exception as e:
            errors.append(str(e))
    conn.commit()
    conn.close()
    return saved, errors


def show():
    render_page_header("Data Penjualan Bulanan", "Input dan perbarui data penjualan per kategori setiap bulan", icon_key="chart", tone="peach")

    # ── Filter bar ────────────────────────────────────────────────────────────
    col_yr, col_mo, col_spacer, col_save = st.columns([1.4, 1.8, 3.8, 1.6], vertical_alignment="bottom")
    with col_yr:
        tahun = st.selectbox("Tahun", options=[2024, 2025, 2026], index=2)
    with col_mo:
        bulan_label = st.selectbox("Bulan", options=list(MONTH_NAMES.values()), index=10)
        bulan = [k for k, v in MONTH_NAMES.items() if v == bulan_label][0]

    df = _get_sales(tahun, bulan)

    with col_save:
        save_btn = st.button("Simpan Data", type="primary", use_container_width=True)

    st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

    # ── Editable table ────────────────────────────────────────────────────────
    with st.container(border=True):
        section_title(f"Data Penjualan — {bulan_label} {tahun}", icon_key="calendar", tone="blue")

        if df.empty:
            st.info("Belum ada kategori aktif. Tambahkan kategori terlebih dahulu.")
            return

        col_cfg = {
            "category_id": None,
            "Kode": st.column_config.TextColumn("Kode", disabled=True, width="small"),
            "Kategori": st.column_config.TextColumn("Kategori", disabled=True, width="medium"),
            "Qty": st.column_config.NumberColumn("Qty", min_value=0, step=1, format="%d", width="small"),
            "Amount (Rp)": st.column_config.NumberColumn(
                "Amount (Rp)", min_value=0, step=1000, format="Rp %,.0f", width="medium"
            ),
        }

        edited_df = st.data_editor(
            df,
            column_config=col_cfg,
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            column_order=["Kode", "Kategori", "Qty", "Amount (Rp)"],
            key=f"sales_editor_{tahun}_{bulan}",
        )

    # ── Summary row ───────────────────────────────────────────────────────────
    total_qty = edited_df["Qty"].sum()
    total_amount = edited_df["Amount (Rp)"].sum()

    st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
    render_kpi_grid([
        {"icon_key": "folder", "value": str(len(edited_df)),       "label": "Total Kategori", "accent": "#7AA9DF", "bg": "#E8F1FB", "text_color": "#3A6BA5"},
        {"icon_key": "box",    "value": f"{int(total_qty):,}",     "label": "Total Qty",      "accent": "#7BC4A4", "bg": "#E6F6EE", "text_color": "#2D6A4F"},
        {"icon_key": "wallet", "value": f"Rp {total_amount:,.0f}", "label": "Total Amount",   "accent": "#E6A97E", "bg": "#FDF1E7", "text_color": "#9C5A2B"},
    ])

    if save_btn:
        saved, errors = _upsert_sales(tahun, bulan, edited_df)
        if errors:
            st.error(f"Terjadi kesalahan: {'; '.join(errors)}")
        else:
            st.success(f"{saved} baris data penjualan berhasil disimpan ke database.")
