"""
views/manajemen_pengguna.py — Halaman Manajemen Pengguna (Pastel Blue Minimalist)
"""
import streamlit as st
from database import get_connection, hash_password
from ui_helpers import render_page_header, pill_badge


def _get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, username, role, status, created_at FROM users ORDER BY id")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def _insert_user(name, username, password, role, status):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (name, username, password, role, status)
            VALUES (?, ?, ?, ?, ?)
        """, (name.strip(), username.strip(), hash_password(password), role, status))
        conn.commit()
        return True, "Pengguna berhasil ditambahkan."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def _update_user(user_id, name, username, role, status, new_password=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if new_password:
            cur.execute("""
                UPDATE users SET name=?, username=?, role=?, status=?, password=?
                WHERE id=?
            """, (name.strip(), username.strip(), role, status, hash_password(new_password), user_id))
        else:
            cur.execute("""
                UPDATE users SET name=?, username=?, role=?, status=?
                WHERE id=?
            """, (name.strip(), username.strip(), role, status, user_id))
        conn.commit()
        return True, "Data pengguna berhasil diperbarui."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def _toggle_status(user_id, current_status):
    new_status = "Nonaktif" if current_status == "Aktif" else "Aktif"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET status=? WHERE id=?", (new_status, user_id))
    conn.commit()
    conn.close()
    return new_status


def _delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# ── Dialogs ───────────────────────────────────────────────────────────────────

@st.dialog("Tambah Pengguna Baru")
def dialog_tambah_user():
    with st.form("form_tambah_user"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nama Lengkap", placeholder="Contoh: Budi Santoso")
        with col2:
            username = st.text_input("Username", placeholder="Contoh: budi")
        col3, col4 = st.columns(2)
        with col3:
            password = st.text_input("Password", type="password", placeholder="Min. 6 karakter")
        with col4:
            confirm_pw = st.text_input("Konfirmasi Password", type="password")
        col5, col6 = st.columns(2)
        with col5:
            role = st.selectbox("Role", ["ADMIN", "PEMILIK", "USER"])
        with col6:
            status = st.selectbox("Status", ["Aktif", "Nonaktif"])

        col_save, col_cancel = st.columns(2)
        with col_save:
            submitted = st.form_submit_button("Simpan", use_container_width=True, type="primary")
        with col_cancel:
            if st.form_submit_button("Batal", use_container_width=True):
                st.rerun()

        if submitted:
            if not name or not username or not password:
                st.error("Semua field wajib diisi.")
            elif len(password) < 6:
                st.error("Password minimal 6 karakter.")
            elif password != confirm_pw:
                st.error("Password dan konfirmasi tidak cocok.")
            else:
                ok, msg = _insert_user(name, username, password, role, status)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error("Username sudah digunakan." if "UNIQUE" in msg else f"Gagal: {msg}")


@st.dialog("Edit Pengguna")
def dialog_edit_user(user: dict):
    with st.form("form_edit_user"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nama Lengkap", value=user["name"])
        with col2:
            username = st.text_input("Username", value=user["username"])
        col3, col4 = st.columns(2)
        with col3:
            new_pw = st.text_input("Password Baru", type="password", placeholder="Kosongkan jika tidak diubah")
        with col4:
            confirm_pw = st.text_input("Konfirmasi Password", type="password")
        col5, col6 = st.columns(2)
        with col5:
            role = st.selectbox(
                "Role", ["ADMIN", "PEMILIK", "USER"],
                index=["ADMIN", "PEMILIK", "USER"].index(user["role"]) if user["role"] in ["ADMIN", "PEMILIK", "USER"] else 0,
            )
        with col6:
            status = st.selectbox("Status", ["Aktif", "Nonaktif"], index=0 if user["status"] == "Aktif" else 1)

        col_save, col_cancel = st.columns(2)
        with col_save:
            submitted = st.form_submit_button("Simpan", use_container_width=True, type="primary")
        with col_cancel:
            if st.form_submit_button("Batal", use_container_width=True):
                st.rerun()

        if submitted:
            if not name or not username:
                st.error("Nama dan Username wajib diisi.")
            elif new_pw and new_pw != confirm_pw:
                st.error("Password baru dan konfirmasi tidak cocok.")
            elif new_pw and len(new_pw) < 6:
                st.error("Password baru minimal 6 karakter.")
            else:
                ok, msg = _update_user(user["id"], name, username, role, status, new_pw if new_pw else None)
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error("Username sudah digunakan." if "UNIQUE" in msg else f"Gagal: {msg}")


@st.dialog("Konfirmasi Hapus Pengguna")
def dialog_hapus_user(user: dict):
    st.warning(f"Apakah Anda yakin ingin menghapus pengguna **{user['name']}** (@{user['username']})?")
    st.caption("Tindakan ini tidak dapat dibatalkan.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ya, Hapus", use_container_width=True, type="primary"):
            _delete_user(user["id"])
            st.rerun()
    with col2:
        if st.button("Batal", use_container_width=True):
            st.rerun()


# ── Main Page ─────────────────────────────────────────────────────────────────

def show():
    render_page_header("Manajemen Pengguna", "Kelola akun dan hak akses pengguna sistem", icon_key="users", tone="lavender")

    user = st.session_state.user
    if user.get("role") not in ("ADMIN",):
        st.error("Halaman ini hanya dapat diakses oleh Administrator.")
        return

    users = _get_users()
    active_count = sum(1 for u in users if u["status"] == "Aktif")

    col_info, col_btn = st.columns([5, 1.8], vertical_alignment="center")
    with col_info:
        st.markdown(f"""
        <div style="display:flex;flex-wrap:wrap;gap:0.5rem 1.5rem;align-items:center;padding:0.25rem 0;font-size:0.85rem;color:#627D98;">
            <span>Total Pengguna: <b style="color:#243B53;">{len(users)}</b></span>
            <span>Aktif: <b style="color:#2D6A4F;">{active_count}</b></span>
            <span>Nonaktif: <b style="color:#9B3B39;">{len(users) - active_count}</b></span>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.button("+ Tambah Pengguna", type="primary", use_container_width=True):
            dialog_tambah_user()

    st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

    if not users:
        st.info("Belum ada data pengguna.")
        return

    current_user_id = user["id"]

    with st.container(border=True):
        h_cols = st.columns([0.45, 1.7, 1.05, 0.95, 0.85, 3.0], vertical_alignment="center")
        for col, h in zip(h_cols, ["No", "Nama Lengkap", "Username", "Role", "Status", "Aksi"]):
            col.markdown(
                f'<div style="font-weight:600;font-size:0.8rem;color:#627D98;'
                f'text-transform:uppercase;letter-spacing:0.03em;padding:0.25rem 0;">{h}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<hr style="border-color:#E2ECF5;margin:0.35rem 0 0.5rem;">', unsafe_allow_html=True)

        for i, u in enumerate(users):
            r_cols = st.columns([0.45, 1.7, 1.05, 0.95, 0.85, 3.0], vertical_alignment="center")
            r_cols[0].markdown(f'<span style="color:#627D98;font-size:0.86rem;">{i+1}</span>', unsafe_allow_html=True)
            r_cols[1].markdown(f'<span style="color:#243B53;font-weight:500;font-size:0.88rem;">{u["name"]}</span>', unsafe_allow_html=True)
            r_cols[2].markdown(f'<span style="color:#627D98;font-family:monospace;font-size:0.83rem;">@{u["username"]}</span>', unsafe_allow_html=True)

            role_tone = "blue" if u["role"] == "ADMIN" else ("lavender" if u["role"] == "PEMILIK" else "neutral")
            r_cols[3].markdown(pill_badge(u["role"], role_tone), unsafe_allow_html=True)

            status_badge = pill_badge("Aktif", "mint") if u["status"] == "Aktif" else pill_badge("Nonaktif", "rose")
            r_cols[4].markdown(status_badge, unsafe_allow_html=True)

            is_self = u["id"] == current_user_id
            with r_cols[5]:
                b1, b2, b3 = st.columns([0.9, 1.35, 1.0], gap="small")
                with b1:
                    if st.button("Edit", key=f"ue_{u['id']}", use_container_width=True):
                        dialog_edit_user(u)
                with b2:
                    lbl = "Nonaktif" if u["status"] == "Aktif" else "Aktifkan"
                    if st.button(lbl, key=f"ut_{u['id']}", disabled=is_self, use_container_width=True):
                        _toggle_status(u["id"], u["status"])
                        st.rerun()
                with b3:
                    if st.button("Hapus", key=f"ud_{u['id']}", disabled=is_self, use_container_width=True):
                        dialog_hapus_user(u)

            if i < len(users) - 1:
                st.markdown('<hr style="border-color:#F0F4F8;margin:0.35rem 0;">', unsafe_allow_html=True)

    st.markdown(
        f'<div style="margin-top:0.5rem;color:#627D98;font-size:0.8rem;">'
        f'Menampilkan {len(users)} pengguna terdaftar</div>',
        unsafe_allow_html=True,
    )
