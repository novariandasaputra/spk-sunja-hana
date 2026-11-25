"""
views/data_kategori.py — Halaman Data Kategori (Pastel Blue Minimalist)
"""
import streamlit as st
from database import get_connection
from ui_helpers import render_page_header, pill_badge

# ── DB helpers ────────────────────────────────────────────────────────────────

def _get_categories(search: str = ""):
    conn = get_connection()
    cur = conn.cursor()
    q = f"%{search}%"
    cur.execute("""
        SELECT id, kode, nama, status
        FROM categories
        WHERE nama LIKE ? OR kode LIKE ?
        ORDER BY kode
    """, (q, q))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def _next_kode():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT kode FROM categories ORDER BY kode DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    if row:
        try:
            return str(int(row["kode"]) + 1).zfill(3)
        except ValueError:
            pass
    return "001"


def _insert_category(kode: str, nama: str, status: str = "Aktif"):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO categories (kode, nama, status) VALUES (?, ?, ?)",
            (kode.strip(), nama.strip(), status)
        )
        conn.commit()
        return True, "Kategori berhasil ditambahkan."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def _update_category(cat_id: int, kode: str, nama: str, status: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE categories SET kode=?, nama=?, status=? WHERE id=?",
            (kode.strip(), nama.strip(), status, cat_id)
        )
        conn.commit()
        return True, "Kategori berhasil diperbarui."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def _deactivate_category(cat_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE categories SET status='Nonaktif' WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()


def _delete_category(cat_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM categories WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()


# ── Dialogs ───────────────────────────────────────────────────────────────────

@st.dialog("Tambah Kategori Baru")
def dialog_tambah():
    next_kode = _next_kode()
    with st.form("form_tambah_kategori"):
        kode = st.text_input("Kode Kategori", value=next_kode, max_chars=10)
        nama = st.text_input("Nama Kategori", placeholder="Contoh: Minuman Dingin")
        status = st.selectbox("Status", ["Aktif", "Nonaktif"])
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Simpan", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("Batal", use_container_width=True):
                st.rerun()
        if submitted:
            if not kode or not nama:
                st.error("Kode dan Nama kategori wajib diisi.")
            else:
                ok, msg = _insert_category(kode, nama, status)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"Gagal: {msg}")


@st.dialog("Edit Kategori")
def dialog_edit(cat: dict):
    with st.form("form_edit_kategori"):
        kode = st.text_input("Kode Kategori", value=cat["kode"], max_chars=10)
        nama = st.text_input("Nama Kategori", value=cat["nama"])
        status = st.selectbox(
            "Status", ["Aktif", "Nonaktif"],
            index=0 if cat["status"] == "Aktif" else 1
        )
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Simpan", use_container_width=True, type="primary")
        with col2:
            if st.form_submit_button("Batal", use_container_width=True):
                st.rerun()
        if submitted:
            if not kode or not nama:
                st.error("Kode dan Nama kategori wajib diisi.")
            else:
                ok, msg = _update_category(cat["id"], kode, nama, status)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"Gagal: {msg}")


@st.dialog("Konfirmasi Hapus")
def dialog_hapus(cat: dict):
    st.warning(f"Apakah Anda yakin ingin menghapus kategori **{cat['nama']}**?")
    st.caption("Tindakan ini tidak dapat dibatalkan. Data penjualan terkait mungkin terpengaruh.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ya, Hapus", use_container_width=True, type="primary"):
            _delete_category(cat["id"])
            st.rerun()
    with col2:
        if st.button("Batal", use_container_width=True):
            st.rerun()


# ── Main Page ─────────────────────────────────────────────────────────────────

def show():
    render_page_header("Data Kategori", "Kelola daftar kategori produk Toko Grosir Sunja Hana", icon_key="folder", tone="mint")

    # ── Toolbar ───────────────────────────────────────────────────────────────
    col_search, col_spacer, col_btn = st.columns([3, 2.2, 2.2], vertical_alignment="center")
    with col_search:
        search = st.text_input(
            "Cari",
            placeholder="Cari kode atau nama kategori...",
            label_visibility="collapsed",
            key="cat_search",
        )
    with col_btn:
        if st.button("+ Tambah Kategori", type="primary", use_container_width=True):
            dialog_tambah()

    st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

    cats = _get_categories(search)
    if not cats:
        st.info("Tidak ada data kategori yang ditemukan.")
        return

    # ── Table Container ───────────────────────────────────────────────────────
    with st.container(border=True):
        # Header Row
        h_cols = st.columns([0.4, 0.7, 2.1, 0.9, 2.9], vertical_alignment="center")
        headers = ["No", "Kode", "Nama Kategori", "Status", "Aksi"]
        for col, h in zip(h_cols, headers):
            col.markdown(
                f'<div style="font-weight:600;font-size:0.8rem;color:#627D98;'
                f'text-transform:uppercase;letter-spacing:0.03em;padding:0.25rem 0;">{h}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="border-color:#E2ECF5;margin:0.35rem 0 0.5rem;">', unsafe_allow_html=True)

        for i, cat in enumerate(cats):
            r_cols = st.columns([0.4, 0.7, 2.1, 0.9, 2.9], vertical_alignment="center")
            r_cols[0].markdown(f'<span style="color:#627D98;font-size:0.86rem;">{i+1}</span>', unsafe_allow_html=True)
            r_cols[1].markdown(
                f'<span style="font-family:monospace;color:#3A6BA5;background:#E6F0FA;'
                f'padding:0.15em 0.5em;border-radius:6px;font-size:0.82rem;font-weight:600;">{cat["kode"]}</span>',
                unsafe_allow_html=True,
            )
            r_cols[2].markdown(f'<span style="color:#243B53;font-weight:500;font-size:0.88rem;">{cat["nama"]}</span>', unsafe_allow_html=True)

            badge = pill_badge("Aktif", "mint") if cat["status"] == "Aktif" else pill_badge("Nonaktif", "rose")
            r_cols[3].markdown(badge, unsafe_allow_html=True)

            with r_cols[4]:
                b_edit, b_del = st.columns([1, 1.4], gap="small")
                with b_edit:
                    if st.button("Edit", key=f"edit_{cat['id']}", use_container_width=True):
                        dialog_edit(cat)
                with b_del:
                    if cat["status"] == "Aktif":
                        if st.button("Nonaktif", key=f"nonaktif_{cat['id']}", use_container_width=True):
                            _deactivate_category(cat["id"])
                            st.rerun()
                    else:
                        if st.button("Hapus", key=f"del_{cat['id']}", use_container_width=True):
                            dialog_hapus(cat)

            if i < len(cats) - 1:
                st.markdown('<hr style="border-color:#F0F4F8;margin:0.35rem 0;">', unsafe_allow_html=True)

    st.markdown(
        f'<div style="margin-top:0.5rem;color:#627D98;font-size:0.8rem;">'
        f'Menampilkan 1 – {len(cats)} dari {len(cats)} kategori</div>',
        unsafe_allow_html=True,
    )
