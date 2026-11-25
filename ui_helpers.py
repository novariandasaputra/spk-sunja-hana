"""
ui_helpers.py — Komponen UI bersama bergaya Pastel Modern + Responsif
"""
import streamlit as st

SVG_ICONS = {
    "logo":      """<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>""",
    "dashboard": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>""",
    "folder":    """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>""",
    "calendar":  """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>""",
    "chart":     """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>""",
    "trend":     """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>""",
    "clock":     """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>""",
    "box":       """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>""",
    "wallet":    """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>""",
    "upload":    """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>""",
    "calc":      """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="8" y1="6" x2="16" y2="6"/><line x1="8" y1="10" x2="8" y2="10.01"/><line x1="12" y1="10" x2="12" y2="10.01"/><line x1="16" y1="10" x2="16" y2="10.01"/><line x1="8" y1="14" x2="8" y2="14.01"/><line x1="12" y1="14" x2="12" y2="14.01"/><line x1="16" y1="14" x2="16" y2="14.01"/><line x1="8" y1="18" x2="16" y2="18"/></svg>""",
    "layers":    """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>""",
    "file":      """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>""",
    "users":     """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
    "award":     """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="7"/><polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/></svg>""",
    "info":      """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>""",
}

TONES = {
    "blue":     ("#E6F1FC", "#3A72B0", "#5B9BD5"),
    "mint":     ("#E3F6EC", "#246A49", "#52B788"),
    "peach":    ("#FEF0E3", "#A0521D", "#F4A261"),
    "lavender": ("#EFEAFA", "#553C9A", "#9D84D8"),
    "rose":     ("#FDECEC", "#9B2C2C", "#E57373"),
    "neutral":  ("#F1F5F9", "#475569", "#94A3B8"),
}


def render_page_header(title: str, subtitle: str = "", icon_key: str = "dashboard", tone: str = "blue"):
    """Render clean colorful pastel page header with modern SVG icon badge."""
    bg, fg, border = TONES.get(tone, TONES["blue"])
    svg = SVG_ICONS.get(icon_key, SVG_ICONS["dashboard"])

    sub_html = (
        f'<div style="color:#64748B;font-size:0.83rem;margin-top:0.1rem;">{subtitle}</div>'
        if subtitle else ""
    )
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.85rem;margin-bottom:0.85rem;flex-wrap:wrap;">
        <div style="width:42px;height:42px;border-radius:11px;background:{bg};
                    color:{fg};border:1px solid {border}40;flex-shrink:0;
                    display:flex;align-items:center;justify-content:center;">
            {svg}
        </div>
        <div style="min-width:0;">
            <h2 style="margin:0;color:#1E293B;font-weight:700;font-size:1.35rem;
                       letter-spacing:-0.01em;white-space:normal;">
                {title}
            </h2>
            {sub_html}
        </div>
    </div>
    """, unsafe_allow_html=True)


def section_title(text: str, icon_key: str = "chart", tone: str = "blue"):
    """Render a clean section title with a small pastel icon badge."""
    bg, fg, _ = TONES.get(tone, TONES["blue"])
    svg = SVG_ICONS.get(icon_key, SVG_ICONS["chart"])
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.55rem;margin-bottom:0.65rem;flex-wrap:wrap;">
        <div style="width:28px;height:28px;border-radius:8px;background:{bg};color:{fg};
                    display:flex;align-items:center;justify-content:center;flex-shrink:0;">
            {svg}
        </div>
        <span style="font-weight:600;color:#1E293B;font-size:0.95rem;">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(col, icon_key: str, value, label: str, accent: str, bg: str, text_color: str):
    """Render KPI card — responsive flex layout."""
    svg = SVG_ICONS.get(icon_key, SVG_ICONS["folder"])
    with col:
        st.markdown(_kpi_card_html(icon_key, value, label, accent, bg, text_color), unsafe_allow_html=True)


def _kpi_card_html(icon_key: str, value, label: str, accent: str, bg: str, text_color: str) -> str:
    svg = SVG_ICONS.get(icon_key, SVG_ICONS["folder"])
    return (
        f'<div class="kpi-card" style="background:linear-gradient(135deg, #FFFFFF 0%, {bg}55 100%);'
        f'border-left:4px solid {accent};">'
        f'<div class="kpi-icon" style="background:{bg}; color:{text_color};">{svg}</div>'
        f'<div style="min-width:0;flex:1;">'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>'
        f'</div></div>'
    )


def render_kpi_grid(items: list):
    """Render a responsive CSS Grid of KPI cards (4 cols desktop -> 2 cols tablet/mobile -> 1 col small mobile)."""
    cards = "".join(
        _kpi_card_html(
            item["icon_key"],
            item["value"],
            item["label"],
            item["accent"],
            item["bg"],
            item["text_color"],
        )
        for item in items
    )
    cls = f"kpi-grid kpi-grid-{len(items)}" if len(items) != 4 else "kpi-grid"
    st.markdown(f'<div class="{cls}">{cards}</div>', unsafe_allow_html=True)


def pill_badge(text: str, tone: str = "blue") -> str:
    """Return HTML for a soft pastel pill badge."""
    bg, fg, _ = TONES.get(tone, TONES["blue"])
    return (
        f'<span style="display:inline-block;background:{bg};color:{fg};'
        f'border-radius:999px;padding:0.2em 0.7em;font-size:0.72rem;'
        f'font-weight:600;white-space:nowrap;">{text}</span>'
    )
