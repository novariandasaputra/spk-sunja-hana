"""
views/import_validasi.py — Halaman Import & Validasi Data (Pastel Blue Minimalist)
"""
import streamlit as st
import pandas as pd
import io
from database import get_connection, get_all_categories
from ui_helpers import render_page_header, section_title

REQUIRED_COLS = {"Kode", "Kategori", "Bulan", "Tahun", "Qty", "Amount"}
MONTH_MAP = {
    "januari": 1, "februari": 2, "maret": 3, "april": 4,
    "mei": 5, "juni": 6, "juli": 7, "agustus": 8,
    "september": 9, "oktober": 10, "november": 11, "desember": 12,
}


def _validate(df: pd.DataFrame, categories: list) -> dict:
    cat_kodes = {c["kode"] for c in categories}
    valid_rows = []
    duplicate_rows = []
    not_found_rows = []
    seen = set()

    for _, row in df.iterrows():
        kode = str(row.get("Kode", "")).strip()
        bulan = str(row.get("Bulan", "")).strip().lower()

        if kode not in cat_kodes:
            not_found_rows.append(row.to_dict())
            continue

        bulan_num = MONTH_MAP.get(bulan)
        if bulan_num is None:
            try:
                bulan_num = int(bulan)
            except ValueError:
                not_found_rows.append(row.to_dict())
                continue

        tahun = int(row.get("Tahun", 2026))
        key = (kode, tahun, bulan_num)

        if key in seen:
            duplicate_rows.append(row.to_dict())
        else:
            seen.add(key)
            valid_rows.append({**row.to_dict(), "_bulan_num": bulan_num, "_tahun": tahun})

    return {
        "valid": valid_rows,
        "duplicates": duplicate_rows,
        "not_found": not_found_rows,
        "total": len(df),
    }


def _do_import(valid_rows: list, categories: list):
    cat_map = {c["kode"]: c["id"] for c in categories}
    conn = get_connection()
    cur = conn.cursor()
    imported = 0
    for row in valid_rows:
        kode = str(row["Kode"]).strip()
        cat_id = cat_map.get(kode)
        tahun = int(row["_tahun"])
        bulan = int(row["_bulan_num"])
        qty = int(row.get("Qty", 0))
        amount = float(str(row.get("Amount", 0)).replace(",", ""))
        cur.execute("""
            INSERT INTO monthly_sales (category_id, tahun, bulan, qty, amount)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(category_id, tahun, bulan)
            DO UPDATE SET qty=excluded.qty, amount=excluded.amount
        """, (cat_id, tahun, bulan, qty, amount))
        imported += 1
    conn.commit()
    conn.close()
    return imported


def _make_template() -> bytes:
    sample = pd.DataFrame({
        "Kode":     ["001", "002", "003"],
        "Kategori": ["Rokok", "Alat Tulis", "Minuman Instan"],
        "Bulan":    ["November", "November", "November"],
        "Tahun":    [2026, 2026, 2026],
        "Qty":      [120, 85, 75],
        "Amount":   [1200000, 850000, 750000],
    })
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        sample.to_excel(writer, index=False, sheet_name="Data Penjualan")
    return buf.getvalue()


def _step_bar(active: int):
    steps = ["1. Upload File", "2. Pratinjau", "3. Validasi", "4. Konfirmasi"]
    cols = st.columns(len(steps), gap="small")
    for i, (col, label) in enumerate(zip(cols, steps), start=1):
        with col:
            if i < active:
                color, bg, border = "#2D6A4F", "#E6F6EE", "#B7E4C7"
            elif i == active:
                color, bg, border = "#1E4976", "#E6F0FA", "#B6D4F2"
            else:
                color, bg, border = "#829AB1", "#FFFFFF", "#E2ECF5"
            weight = "600" if i <= active else "500"
            st.markdown(f"""
            <div style="text-align:center;padding:0.55rem 0.5rem;border-radius:8px;
                        background:{bg};color:{color};border:1px solid {border};
                        font-weight:{weight};font-size:0.82rem;">
                {label}
            </div>
            """, unsafe_allow_html=True)


def show():
    render_page_header("Import & Validasi Data", "Unggah dan validasi data penjualan dari file Excel", icon_key="upload", tone="blue")

    for key, default in [
        ("iv_step", 1),
        ("iv_df", None),
        ("iv_validation", None),
        ("iv_imported", False),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    step = st.session_state.iv_step
    _step_bar(step)
    st.markdown("<div style='margin-top:1.1rem;'></div>", unsafe_allow_html=True)

    categories = get_all_categories()

    # ── STEP 1: Upload File ───────────────────────────────────────────────────
    if step == 1:
        col_main, col_tip = st.columns([3, 2], gap="large")

        with col_main:
            with st.container(border=True):
                section_title("Upload File Excel", icon_key="upload", tone="blue")

                uploaded = st.file_uploader(
                    "Pilih file .xlsx atau .xls",
                    type=["xlsx", "xls"],
                    help="Format kolom: Kode | Kategori | Bulan | Tahun | Qty | Amount",
                    label_visibility="collapsed",
                )

                st.markdown(
                    '<p style="color:#64748B;font-size:0.78rem;margin-top:0.4rem;margin-bottom:0;">'
                    'Drag & drop file Excel di sini atau klik Browse files. Format yang didukung: .xlsx, .xls</p>',
                    unsafe_allow_html=True,
                )

            if uploaded:
                try:
                    df = pd.read_excel(uploaded)
                    st.session_state.iv_df = df
                    missing = REQUIRED_COLS - set(df.columns)
                    if missing:
                        st.error(f"Kolom wajib tidak ditemukan: {', '.join(missing)}")
                    else:
                        st.success(f"File berhasil dibaca: {len(df)} baris data terdeteksi.")
                        if st.button("Lanjutkan ke Pratinjau", type="primary", use_container_width=True):
                            st.session_state.iv_step = 2
                            st.rerun()
                except Exception as e:
                    st.error(f"Gagal membaca file: {e}")

        with col_tip:
            st.markdown("""
            <div style="background:#E6F0FA;border:1px solid #C8DDF3;border-radius:12px;
                        padding:1.25rem 1.4rem;font-size:0.83rem;color:#243B53;">
                <div style="font-weight:600;color:#1E4976;margin-bottom:0.5rem;">Panduan Format File</div>
                <ul style="margin:0;padding-left:1.2rem;line-height:1.9;color:#486581;">
                    <li><b>Kode</b>: Kode kategori (mis. 001)</li>
                    <li><b>Kategori</b>: Nama kategori</li>
                    <li><b>Bulan</b>: Nama bulan (mis. November)</li>
                    <li><b>Tahun</b>: Tahun (mis. 2026)</li>
                    <li><b>Qty</b>: Jumlah penjualan</li>
                    <li><b>Amount</b>: Total nilai (angka)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)
            tmpl = _make_template()
            st.download_button(
                "Unduh Template Excel",
                data=tmpl,
                file_name="template_import_spk.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

    # ── STEP 2: Pratinjau ─────────────────────────────────────────────────────
    elif step == 2:
        df = st.session_state.iv_df
        st.markdown("""
        <div class="soft-card">
            <div style="font-weight:600;color:#243B53;font-size:0.95rem;margin-bottom:0.75rem;">
                Pratinjau Data (10 baris pertama)
            </div>
        """, unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)
        st.markdown(f"<p style='color:#627D98;font-size:0.8rem;margin:0.5rem 0 0;'>Total: {len(df)} baris</p></div>",
                    unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Kembali", use_container_width=True):
                st.session_state.iv_step = 1
                st.rerun()
        with col2:
            if st.button("Validasi Data", type="primary", use_container_width=True):
                result = _validate(df, categories)
                st.session_state.iv_validation = result
                st.session_state.iv_step = 3
                st.rerun()

    # ── STEP 3: Validasi ──────────────────────────────────────────────────────
    elif step == 3:
        result = st.session_state.iv_validation
        col_res, col_prev = st.columns(2, gap="large")

        with col_res:
            st.markdown("""
            <div class="soft-card">
                <div style="font-weight:600;color:#243B53;margin-bottom:0.9rem;">Hasil Validasi</div>
            """, unsafe_allow_html=True)

            items = [
                ("Data valid",           len(result["valid"]),      "#2D6A4F", "#E6F6EE"),
                ("Duplikat",             len(result["duplicates"]), "#9C5A2B", "#FDF1E7"),
                ("Data tidak ditemukan", len(result["not_found"]),  "#9B3B39", "#FBECEC"),
            ]
            for label, count, color, bg in items:
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                            padding:0.65rem 0.9rem;border-radius:8px;background:{bg};
                            margin-bottom:0.5rem;">
                    <span style="font-size:0.85rem;color:{color};font-weight:500;">{label}</span>
                    <span style="font-weight:700;color:{color};font-size:0.95rem;">{count} baris</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_prev:
            if result["not_found"] or result["duplicates"]:
                st.markdown("""
                <div class="soft-card">
                    <div style="font-weight:600;color:#9B3B39;margin-bottom:0.75rem;">
                        Data Bermasalah
                    </div>
                """, unsafe_allow_html=True)
                problem_df = pd.DataFrame(result["not_found"] + result["duplicates"])
                disp_cols = [c for c in ["Kode", "Kategori", "Bulan", "Tahun"] if c in problem_df.columns]
                st.dataframe(problem_df[disp_cols].head(5), hide_index=True, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background:#E6F6EE;border:1px solid #B7E4C7;border-radius:12px;
                            padding:2.25rem;text-align:center;">
                    <div style="font-weight:600;color:#2D6A4F;font-size:1rem;">
                        Semua data valid
                    </div>
                    <div style="color:#40916C;font-size:0.82rem;margin-top:0.25rem;">
                        Data siap untuk diimport ke database.
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Kembali ke Pratinjau", use_container_width=True):
                st.session_state.iv_step = 2
                st.rerun()
        with col2:
            disabled = len(result["valid"]) == 0
            lbl = f"Lanjutkan ke Import ({len(result['valid'])} baris valid)"
            if st.button(lbl, type="primary", use_container_width=True, disabled=disabled):
                st.session_state.iv_step = 4
                st.rerun()

    # ── STEP 4: Konfirmasi & Import ───────────────────────────────────────────
    elif step == 4:
        result = st.session_state.iv_validation
        st.markdown("""
        <div class="soft-card" style="text-align:center;">
            <div style="font-weight:700;font-size:1.05rem;color:#243B53;margin-bottom:1rem;">
                Konfirmasi Import Data
            </div>
        """, unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem;background:#E6F6EE;border-radius:10px;">
                <div style="font-size:1.8rem;font-weight:700;color:#2D6A4F;">{len(result['valid'])}</div>
                <div style="color:#2D6A4F;font-size:0.82rem;">Baris akan diimport</div>
            </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown(f"""
            <div style="text-align:center;padding:1rem;background:#FDF1E7;border-radius:10px;">
                <div style="font-size:1.8rem;font-weight:700;color:#9C5A2B;">{len(result['duplicates']) + len(result['not_found'])}</div>
                <div style="color:#9C5A2B;font-size:0.82rem;">Baris diabaikan</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <p style="color:#627D98;font-size:0.82rem;margin-top:0.85rem;margin-bottom:0;">
            Data pada periode yang sama akan diperbarui secara otomatis.
        </p></div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)

        if st.session_state.iv_imported:
            st.success("Import selesai. Data telah berhasil disimpan ke database.")
            if st.button("Import Data Baru", type="primary", use_container_width=True):
                st.session_state.iv_step = 1
                st.session_state.iv_df = None
                st.session_state.iv_validation = None
                st.session_state.iv_imported = False
                st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Kembali", use_container_width=True):
                    st.session_state.iv_step = 3
                    st.rerun()
            with col2:
                if st.button("Konfirmasi & Import", type="primary", use_container_width=True):
                    with st.spinner("Mengimport data..."):
                        _do_import(result["valid"], categories)
                    st.session_state.iv_imported = True
                    st.rerun()
