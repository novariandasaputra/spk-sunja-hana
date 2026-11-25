import streamlit as st
import sys
import os

# ── Path setup ──────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, get_user
from ui_helpers import SVG_ICONS

# ── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="SPK Sunja Hana",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Initialize DB (once per session) ─────────────────────────────────────────
if not st.session_state.get("db_initialized"):
    init_db()
    st.session_state.db_initialized = True

# ── Load CSS (cached) ─────────────────────────────────────────────────────────
@st.cache_data
def _read_css(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        st.markdown(f"<style>{_read_css(css_path)}</style>", unsafe_allow_html=True)

load_css()

# ── Session state defaults ────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# ── Navigation map ────────────────────────────────────────────────────────────
# (svg_path_d, label, page_name, module_path)
NAV_ITEMS = [
    ("dashboard",  "Dashboard",  "Dashboard",              "views.dashboard"),
    ("folder",     "Kategori",   "Data Kategori",          "views.data_kategori"),
    ("calendar",   "Penjualan",  "Data Penjualan",         "views.data_penjualan"),
    ("upload",     "Import",     "Import & Validasi",      "views.import_validasi"),
    ("calc",       "Analisis",   "Analisis CRITIC-TOPSIS", "views.analisis_critic_topsis"),
    ("chart",      "Hasil",      "Hasil Analisis",         "views.hasil_analisis"),
    ("layers",     "Detail",     "Detail Perhitungan",     "views.detail_perhitungan"),
    ("clock",      "Riwayat",    "Riwayat Analisis",       "views.riwayat_analisis"),
    ("file",       "Laporan",    "Laporan",                "views.laporan"),
    ("users",      "Pengguna",   "Manajemen Pengguna",     "views.manajemen_pengguna"),
]

# ── SVG inline icons for navbar ───────────────────────────────────────────────
NAV_SVGS = {
    "dashboard": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/></svg>',
    "folder":    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>',
    "calendar":  '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "upload":    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>',
    "calc":      '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="8" y2="10.01"/><line x1="12" y1="10" x2="12" y2="10.01"/><line x1="16" y1="10" x2="16" y2="10.01"/><line x1="8" y1="14" x2="8" y2="14.01"/><line x1="12" y1="14" x2="12" y2="14.01"/><line x1="16" y1="14" x2="16" y2="14.01"/><line x1="8" y1="18" x2="16" y2="18"/></svg>',
    "chart":     '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "layers":    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>',
    "clock":     '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "file":      '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "users":     '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
}

# ── Login Page ────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #EAF2FB 0%, #F4F7FB 100%) !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:3rem;'></div>", unsafe_allow_html=True)
    _, col_card, _ = st.columns([0.8, 3.0, 0.8])

    with col_card:
        with st.container(border=True):
            col_left, col_right = st.columns([1.05, 1.15], gap="medium", vertical_alignment="center")

            with col_left:
                st.markdown("""
                <div class="login-left-panel">
                    <svg class="login-left-bg" viewBox="0 0 400 440" preserveAspectRatio="xMidYMid slice"
                         xmlns="http://www.w3.org/2000/svg">
                        <!-- Background pattern: shelves perspective -->
                        <g stroke="#1E3A5F" stroke-width="1.8" fill="none" opacity="0.7">
                            <line x1="20" y1="70" x2="160" y2="115"/>
                            <line x1="20" y1="145" x2="160" y2="168"/>
                            <line x1="20" y1="218" x2="160" y2="220"/>
                            <line x1="20" y1="288" x2="160" y2="272"/>
                            <line x1="380" y1="58" x2="240" y2="115"/>
                            <line x1="380" y1="136" x2="240" y2="168"/>
                            <line x1="380" y1="214" x2="240" y2="220"/>
                            <line x1="380" y1="290" x2="240" y2="272"/>
                            <!-- Boxes left shelf -->
                            <rect x="30" y="82" width="34" height="34" rx="4" fill="#FFFFFF" fill-opacity="0.4"/>
                            <rect x="72" y="94" width="28" height="28" rx="4" fill="#FFFFFF" fill-opacity="0.3"/>
                            <rect x="108" y="88" width="38" height="30" rx="4" fill="#FFFFFF" fill-opacity="0.25"/>
                            <rect x="30" y="156" width="30" height="38" rx="4" fill="#FFFFFF" fill-opacity="0.3"/>
                            <rect x="68" y="160" width="40" height="32" rx="4" fill="#FFFFFF" fill-opacity="0.2"/>
                            <!-- Boxes right shelf -->
                            <rect x="264" y="80" width="38" height="40" rx="4" fill="#FFFFFF" fill-opacity="0.3"/>
                            <rect x="310" y="68" width="32" height="48" rx="4" fill="#FFFFFF" fill-opacity="0.4"/>
                            <rect x="348" y="76" width="22" height="42" rx="4" fill="#FFFFFF" fill-opacity="0.25"/>
                            <rect x="262" y="155" width="42" height="34" rx="4" fill="#FFFFFF" fill-opacity="0.25"/>
                            <rect x="314" y="150" width="34" height="38" rx="4" fill="#FFFFFF" fill-opacity="0.2"/>
                        </g>
                        <!-- Shopping cart center -->
                        <g transform="translate(132, 230)" stroke="#1E3A5F" stroke-width="3.5"
                           stroke-linecap="round" stroke-linejoin="round" fill="none">
                            <path d="M8 8 L32 8 L52 90 L148 90 L168 32 L44 32"/>
                            <line x1="52" y1="52" x2="160" y2="52"/>
                            <line x1="55" y1="72" x2="153" y2="72"/>
                            <line x1="84" y1="32" x2="84" y2="90"/>
                            <line x1="118" y1="32" x2="118" y2="90"/>
                            <circle cx="72" cy="112" r="11"/>
                            <circle cx="136" cy="112" r="11"/>
                        </g>
                    </svg>
                    <div class="login-left-content">
                        <div style="display:flex;align-items:center;gap:0.6rem;">
                            <div style="width:34px;height:34px;border-radius:9px;background:rgba(255,255,255,0.85);
                                        display:flex;align-items:center;justify-content:center;
                                        box-shadow:0 2px 8px rgba(30,58,95,0.12);">
                                <svg width="17" height="17" viewBox="0 0 24 24" fill="none"
                                     stroke="#1E4976" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                                    <polyline points="9 22 9 12 15 12 15 22"/>
                                </svg>
                            </div>
                            <span style="font-size:0.76rem;font-weight:700;letter-spacing:0.08em;color:#1E3A5F;">
                                SPK SUNJA HANA
                            </span>
                        </div>
                        <div style="margin:1.75rem 0 1rem;">
                            <div style="width:44px;height:44px;border-radius:12px;
                                        background:rgba(255,255,255,0.88);
                                        display:flex;align-items:center;justify-content:center;
                                        margin-bottom:1rem;box-shadow:0 2px 10px rgba(30,58,95,0.10);">
                                <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                                     stroke="#1E4976" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
                                    <polyline points="17 6 23 6 23 12"/>
                                </svg>
                            </div>
                            <h2 style="color:#1E293B;font-weight:700;font-size:1.5rem;
                                       line-height:1.25;margin:0 0 0.55rem;">
                                SPK Prioritas<br>Pengadaan Kategori
                            </h2>
                            <p style="color:#334E68;font-size:0.82rem;margin:0;line-height:1.55;">
                                Toko Grosir Sunja Hana &bull; Analisis CRITIC-TOPSIS
                            </p>
                        </div>
                        <div style="font-size:0.73rem;color:#3A5A80;font-weight:500;">
                            Sistem Pendukung Keputusan v1.0
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_right:
                st.markdown("""
                <div style="padding:0.5rem 0.75rem 0.5rem;">
                    <h3 style="color:#1E293B;font-weight:700;font-size:1.45rem;margin:0 0 0.2rem;">
                        Masuk ke Sistem
                    </h3>
                    <p style="color:#627D98;font-size:0.84rem;margin:0 0 1.25rem;">
                        Silakan login untuk melanjutkan ke dashboard analitik.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="login-form-bare">', unsafe_allow_html=True)
                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="Masukkan username")
                    password = st.text_input("Password", type="password", placeholder="Masukkan password")
                    st.markdown("<div style='margin-top:0.4rem;'></div>", unsafe_allow_html=True)
                    submitted = st.form_submit_button(
                        "Masuk ke Dashboard",
                        use_container_width=True,
                        type="primary",
                    )
                    if submitted:
                        if not username or not password:
                            st.error("Username dan password tidak boleh kosong.")
                        else:
                            user = get_user(username, password)
                            if user:
                                st.session_state.logged_in = True
                                st.session_state.user = user
                                st.session_state.current_page = "Dashboard"
                                st.rerun()
                            else:
                                st.error("Username atau password salah, atau akun tidak aktif.")
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("""
                <hr style="border-color:#E2ECF5;margin:1rem 0.75rem 0.6rem;">
                <div style="display:flex;justify-content:space-between;padding:0 0.75rem;
                            font-size:0.75rem;color:#94A3B8;">
                    <span>Akses terbatas untuk staf terdaftar</span>
                    <span>v1.0</span>
                </div>
                """, unsafe_allow_html=True)


# ── Top Navbar ────────────────────────────────────────────────────────────────
def show_top_navbar():
    user = st.session_state.user
    role_bg  = "#E6F1FC" if user.get("role") == "ADMIN" else "#EFEAFA"
    role_fg  = "#3A72B0" if user.get("role") == "ADMIN" else "#553C9A"
    role_dot = "#5B9BD5" if user.get("role") == "ADMIN" else "#9D84D8"
    cur_page = st.session_state.current_page

    with st.container(border=True):
        # ── Baris 1: Brand + User + Keluar ───────────────────────────────────
        b_brand, b_user, b_out = st.columns([5, 3.2, 1.2], vertical_alignment="center")

        with b_brand:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:0.7rem;">
                <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
                            background:linear-gradient(135deg,#E6F1FC,#C8DDF3);
                            border:1px solid #C8DDF3;
                            display:flex;align-items:center;justify-content:center;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3A72B0"
                         stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                        <polyline points="9 22 9 12 15 12 15 22"/>
                    </svg>
                </div>
                <div>
                    <div style="font-weight:700;font-size:0.97rem;color:#1E293B;line-height:1.2;">SPK Sunja Hana</div>
                    <div style="font-size:0.70rem;color:#94A3B8;">Prioritas Pengadaan &bull; CRITIC-TOPSIS</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with b_user:
            st.markdown(f"""
            <div class="user-pill-wrap" style="text-align:right;">
                <span style="display:inline-flex;align-items:center;gap:0.45rem;
                             background:#F8FAFC;border:1px solid #E2ECF5;border-radius:999px;
                             padding:0.28rem 0.75rem;font-size:0.78rem;color:#1E293B;font-weight:500;
                             white-space:nowrap;">
                    <span style="width:6px;height:6px;border-radius:50%;
                                 background:{role_dot};display:inline-block;flex-shrink:0;"></span>
                    {user['name']}
                    <span style="background:{role_bg};color:{role_fg};border-radius:999px;
                                 padding:0.1em 0.5em;font-size:0.65rem;font-weight:600;">{user['role']}</span>
                </span>
            </div>
            """, unsafe_allow_html=True)

        with b_out:
            if st.button("Keluar", key="top_logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.current_page = "Dashboard"
                st.rerun()

        st.markdown('<hr style="border-color:#EEF2F7;margin:0.45rem 0 0.4rem;">', unsafe_allow_html=True)

        # ── Nav Baris Tunggal (10 tombol, 1 baris) ────────────────────────────
        nav_cols = st.columns(10, gap="small")
        for col, (_, label, page_name, _) in zip(nav_cols, NAV_ITEMS):
            with col:
                if st.button(
                    label,
                    key=f"nav_{page_name}",
                    type="primary" if cur_page == page_name else "secondary",
                    use_container_width=True,
                ):
                    st.session_state.current_page = page_name
                    st.rerun()

    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)


# ── Page Router ───────────────────────────────────────────────────────────────
def route_page():
    page = st.session_state.current_page
    module_map = {page_name: mod for _, _, page_name, mod in NAV_ITEMS}
    module_path = module_map.get(page, "views.dashboard")

    try:
        import importlib
        mod = importlib.import_module(module_path)
        if hasattr(mod, "show"):
            mod.show()
        else:
            st.warning(f"Halaman '{page}' belum memiliki fungsi show().")
    except ModuleNotFoundError as e:
        st.info(f"Halaman **{page}** sedang dalam pengembangan. ({e})")
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat halaman: {e}")
        import traceback
        st.code(traceback.format_exc())


# ── Main Entry Point ──────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        show_login()
    else:
        show_top_navbar()
        route_page()


if __name__ == "__main__":
    main()
