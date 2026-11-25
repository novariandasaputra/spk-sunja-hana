"""
views/laporan.py — Halaman 10: Laporan (Pastel Blue Minimalist)
Mendukung ekspor ke Excel (.xlsx) dan PDF (.pdf).
"""
import streamlit as st
import io
from datetime import datetime
from database import get_latest_analysis
from ui_helpers import render_page_header, section_title


def _generate_excel(result: dict) -> bytes:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    wb = openpyxl.Workbook()
    navy = "4A76A8"
    blue = "6B9BD2"
    grey = "F6F9FC"

    sub_font = Font(bold=True, color="FFFFFF", size=10)
    sub_fill = PatternFill("solid", fgColor=blue)
    alt_fill = PatternFill("solid", fgColor=grey)
    center = Alignment(horizontal="center", vertical="center")
    thin = Side(style="thin", color="D5E4F4")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    aid = result.get("analysis_id", "—")
    period = result.get("periode_label", "—")
    rankings = result.get("rankings", [])
    dm = result.get("decision_matrix", {})
    critic = result.get("critic", {})
    alts = dm.get("index", [])
    cols_l = dm.get("labels", [])

    # Sheet 1: Ringkasan
    ws1 = wb.active
    ws1.title = "Ringkasan"
    ws1.merge_cells("A1:G1")
    c = ws1["A1"]
    c.value = "LAPORAN ANALISIS SPK SUNJA HANA"
    c.font = Font(bold=True, size=14, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=navy)
    c.alignment = center

    ws1.merge_cells("A2:G2")
    c2 = ws1["A2"]
    c2.value = f"Periode: {period}   |   ID Analisis: {aid}"
    c2.font = Font(bold=True, size=10, color="FFFFFF")
    c2.fill = PatternFill("solid", fgColor=blue)
    c2.alignment = center

    ws1.row_dimensions[1].height = 25
    ws1.row_dimensions[2].height = 18
    ws1["A4"] = "Dibuat:"
    ws1["B4"] = datetime.now().strftime("%d %B %Y, %H:%M")

    hdr = ["Peringkat", "Kode", "Nama Kategori", "D+", "D-", "Nilai Preferensi (Vi)", "Keterangan"]
    for col_i, h in enumerate(hdr, start=1):
        cell = ws1.cell(row=6, column=col_i, value=h)
        cell.font = sub_font
        cell.fill = sub_fill
        cell.alignment = center
        cell.border = border

    prio_map = {1: "Prioritas Utama", 2: "Prioritas Tinggi", 3: "Prioritas Tinggi", 4: "Prioritas Menengah"}
    for ri, r in enumerate(rankings):
        row_num = 7 + ri
        values = [
            r["rank"], r["kode"], r["nama"],
            r["d_plus"], r["d_minus"], r["nilai_preferensi"],
            prio_map.get(r["rank"], "Prioritas Rendah"),
        ]
        fill = alt_fill if ri % 2 == 1 else PatternFill()
        for ci, val in enumerate(values, start=1):
            cell = ws1.cell(row=row_num, column=ci, value=val)
            cell.fill = fill
            cell.border = border
            cell.alignment = center

    for col_i, w in enumerate([12, 8, 20, 12, 12, 20, 18], start=1):
        ws1.column_dimensions[get_column_letter(col_i)].width = w

    # Sheet 2: Matriks Keputusan
    ws2 = wb.create_sheet("Matriks Keputusan")
    ws2.merge_cells("A1:F1")
    ws2["A1"].value = "Matriks Keputusan Awal"
    ws2["A1"].font = Font(bold=True, size=12, color="FFFFFF")
    ws2["A1"].fill = PatternFill("solid", fgColor=navy)
    ws2["A1"].alignment = center

    hdr2 = ["Alternatif"] + cols_l
    for ci, h in enumerate(hdr2, start=1):
        cell = ws2.cell(row=2, column=ci, value=h)
        cell.font = sub_font
        cell.fill = sub_fill
        cell.alignment = center
        cell.border = border

    for ri, (alt, row_data) in enumerate(zip(alts, dm.get("data", []))):
        fill = alt_fill if ri % 2 == 1 else PatternFill()
        ws2.cell(row=3 + ri, column=1, value=alt).border = border
        for ci, val in enumerate(row_data, start=2):
            cell = ws2.cell(row=3 + ri, column=ci, value=round(val, 4))
            cell.border = border
            cell.fill = fill
            cell.alignment = center

    for ci in range(1, len(hdr2) + 1):
        ws2.column_dimensions[get_column_letter(ci)].width = 18

    # Sheet 3: Bobot CRITIC
    ws3 = wb.create_sheet("Bobot CRITIC")
    ws3.merge_cells("A1:F1")
    ws3["A1"].value = "Bobot CRITIC"
    ws3["A1"].font = Font(bold=True, size=12, color="FFFFFF")
    ws3["A1"].fill = PatternFill("solid", fgColor=navy)
    ws3["A1"].alignment = center

    hdr3 = ["Kriteria", "Std Dev", "Conflict", "Information (Cj)", "Bobot (wj)"]
    for ci, h in enumerate(hdr3, start=1):
        cell = ws3.cell(row=2, column=ci, value=h)
        cell.font = sub_font
        cell.fill = sub_fill
        cell.alignment = center
        cell.border = border

    for ri, (lbl, sd, conf, info, w) in enumerate(zip(
        cols_l, critic.get("std_dev", []), critic.get("conflict", []),
        critic.get("information", []), critic.get("weights", []),
    )):
        fill = alt_fill if ri % 2 == 1 else PatternFill()
        for ci, val in enumerate([lbl, sd, conf, info, w], start=1):
            cell = ws3.cell(row=3 + ri, column=ci, value=round(val, 6) if isinstance(val, float) else val)
            cell.border = border
            cell.fill = fill
            cell.alignment = center

    for ci, w in enumerate([22, 14, 18, 18, 12], start=1):
        ws3.column_dimensions[get_column_letter(ci)].width = w

    # Sheet 4: TOPSIS
    ws4 = wb.create_sheet("TOPSIS")
    ws4.merge_cells("A1:F1")
    ws4["A1"].value = "Hasil TOPSIS — Jarak & Nilai Preferensi"
    ws4["A1"].font = Font(bold=True, size=12, color="FFFFFF")
    ws4["A1"].fill = PatternFill("solid", fgColor=navy)
    ws4["A1"].alignment = center

    hdr4 = ["Alternatif", "D+ (ke PIS)", "D- (ke NIS)", "Nilai Preferensi (Vi)", "Peringkat"]
    for ci, h in enumerate(hdr4, start=1):
        cell = ws4.cell(row=2, column=ci, value=h)
        cell.font = sub_font
        cell.fill = sub_fill
        cell.alignment = center
        cell.border = border

    for ri, r in enumerate(rankings):
        fill = alt_fill if ri % 2 == 1 else PatternFill()
        for ci, val in enumerate([r["nama"], r["d_plus"], r["d_minus"], r["nilai_preferensi"], r["rank"]], start=1):
            cell = ws4.cell(row=3 + ri, column=ci, value=round(val, 6) if isinstance(val, float) else val)
            cell.border = border
            cell.fill = fill
            cell.alignment = center

    for ci, w in enumerate([22, 16, 16, 22, 10], start=1):
        ws4.column_dimensions[get_column_letter(ci)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _clean_pdf_text(s) -> str:
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)
    replacements = {
        "—": "-", "–": "-", "⁺": "+", "⁻": "-",
        "•": "*", "✓": "V", "✔": "V",
        "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...",
    }
    for orig, rep in replacements.items():
        s = s.replace(orig, rep)
    return s.encode("latin-1", "replace").decode("latin-1")


def _generate_pdf(result: dict) -> bytes:
    try:
        from fpdf import FPDF
    except ImportError:
        return b""

    aid = _clean_pdf_text(result.get("analysis_id", "-"))
    period = _clean_pdf_text(result.get("periode_label", "-"))
    rankings = result.get("rankings", [])
    dm = result.get("decision_matrix", {})
    critic = result.get("critic", {})
    cols_l = [_clean_pdf_text(lbl) for lbl in dm.get("labels", [])]

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(74, 118, 168)
            self.rect(0, 0, 210, 18, "F")
            self.set_text_color(255, 255, 255)
            self.set_font("Helvetica", "B", 11)
            self.set_xy(10, 4)
            self.cell(0, 10, "SPK Prioritas Pengadaan Kategori Produk - Sunja Hana", ln=False)
            self.set_text_color(0, 0, 0)
            self.ln(18)

        def footer(self):
            self.set_y(-13)
            self.set_font("Helvetica", "", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 10, f"Halaman {self.page_no()} | Dicetak: {datetime.now().strftime('%d %B %Y %H:%M')}", align="C")

    pdf = PDF()
    pdf.set_margins(14, 22, 14)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_fill_color(107, 155, 210)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "LAPORAN ANALISIS CRITIC-TOPSIS", ln=True, align="C", fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Periode: {period}   |   ID: {aid}   |   Tanggal: {datetime.now().strftime('%d %B %Y')}", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(230, 240, 250)
    pdf.cell(0, 8, "1. Ringkasan Hasil", ln=True, fill=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(74, 118, 168)
    pdf.set_text_color(255, 255, 255)
    col_ws = [15, 55, 25, 25, 32, 30]
    headers = ["No", "Nama Kategori", "D+", "D-", "Nilai Preferensi", "Keterangan"]
    for w, h in zip(col_ws, headers):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()

    prio_map = {1: "Prioritas Utama", 2: "Prioritas Tinggi", 3: "Prioritas Tinggi", 4: "Prioritas Menengah"}
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    for ri, r in enumerate(rankings):
        fill = ri % 2 == 1
        if fill:
            pdf.set_fill_color(246, 249, 252)
        for w, val in zip(col_ws, [
            r["rank"], _clean_pdf_text(r["nama"]),
            f"{r['d_plus']:.4f}", f"{r['d_minus']:.4f}",
            f"{r['nilai_preferensi']:.4f}",
            prio_map.get(r["rank"], "Rendah"),
        ]):
            pdf.cell(w, 6, str(val), border=1, align="C", fill=fill)
        pdf.ln()

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(230, 240, 250)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "2. Bobot CRITIC", ln=True, fill=True)
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(74, 118, 168)
    pdf.set_text_color(255, 255, 255)
    w_critic = [60, 30, 35, 35, 22]
    hdr_c = ["Kriteria", "Std Dev", "Conflict", "Information", "Bobot"]
    for w, h in zip(w_critic, hdr_c):
        pdf.cell(w, 7, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(0, 0, 0)
    for ri, (lbl, sd, conf, info, w_val) in enumerate(zip(
        cols_l, critic.get("std_dev", []), critic.get("conflict", []),
        critic.get("information", []), critic.get("weights", []),
    )):
        fill = ri % 2 == 1
        if fill:
            pdf.set_fill_color(246, 249, 252)
        for w, val in zip(w_critic, [lbl, f"{sd:.4f}", f"{conf:.4f}", f"{info:.4f}", f"{w_val:.4f}"]):
            pdf.cell(w, 6, str(val), border=1, align="C", fill=fill)
        pdf.ln()

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0, 5,
        "Laporan ini dibuat secara otomatis oleh Sistem Pendukung Keputusan SPK Sunja Hana.\n"
        "Metode: CRITIC (pembobotan objektif) + TOPSIS (perankingan).",
    )

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def show():
    render_page_header("Laporan Hasil Analisis", "Pratinjau dan ekspor laporan hasil analisis ke Excel atau PDF", icon_key="file", tone="blue")

    if st.session_state.get("current_analysis"):
        result = st.session_state.current_analysis
    else:
        rec = get_latest_analysis()
        result = rec.get("result_data", {}) if rec else {}

    if not result or "rankings" not in result:
        st.info("Belum ada hasil analisis. Jalankan analisis melalui menu **Analisis CRITIC-TOPSIS** terlebih dahulu.")
        return

    aid = result.get("analysis_id", st.session_state.get("current_analysis_id", "—"))
    period = result.get("periode_label", "—")

    col_left, col_right = st.columns([1.5, 2.5], gap="large")

    with col_left:
        with st.container(border=True):
            section_title("Pilih Format Laporan", icon_key="file", tone="blue")
            fmt = st.radio("Format", ["Excel (.xlsx)", "PDF (.pdf)"], label_visibility="collapsed")
        st.markdown("<div style='margin-top:0.75rem;'></div>", unsafe_allow_html=True)

        if fmt == "Excel (.xlsx)":
            excel_bytes = _generate_excel(result)
            fname = f"Laporan_SPK_{aid}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            st.download_button(
                label="Unduh Laporan Excel",
                data=excel_bytes,
                file_name=fname,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
            )
            st.caption("4 sheet: Ringkasan, Matriks Keputusan, Bobot CRITIC, TOPSIS")
        else:
            pdf_available = True
            try:
                import fpdf  # noqa: F401
            except ImportError:
                pdf_available = False

            if pdf_available:
                pdf_bytes = _generate_pdf(result)
                if pdf_bytes:
                    fname = f"Laporan_SPK_{aid}_{datetime.now().strftime('%Y%m%d')}.pdf"
                    st.download_button(
                        label="Unduh Laporan PDF",
                        data=pdf_bytes,
                        file_name=fname,
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                    )
                else:
                    st.error("Gagal menghasilkan PDF. Coba format Excel.")
            else:
                st.warning("Library `fpdf2` belum terinstal.")

    with col_right:
        rankings = result.get("rankings", [])
        rank_rows = "".join([
            f"<tr style='background:{'#F6F9FC' if i%2==1 else 'white'};'>"
            f"<td style='padding:0.45rem 0.6rem;text-align:center;color:#486581;'>{r['rank']}</td>"
            f"<td style='padding:0.45rem 0.6rem;color:#243B53;font-weight:500;'>{r['nama']}</td>"
            f"<td style='padding:0.45rem 0.6rem;text-align:center;color:#3A6BA5;font-weight:600;'>{r['nilai_preferensi']:.4f}</td>"
            f"</tr>"
            for i, r in enumerate(rankings)
        ])

        weights = result.get("critic", {}).get("weights", [])
        dm = result.get("decision_matrix", {})
        cols_l = dm.get("labels", [])
        w_rows = "".join([
            f"<tr style='background:{'#F6F9FC' if i%2==1 else 'white'};'>"
            f"<td style='padding:0.45rem 0.6rem;color:#243B53;'>{lbl}</td>"
            f"<td style='padding:0.45rem 0.6rem;text-align:center;color:#3A6BA5;font-weight:600;'>{w:.4f}</td>"
            f"</tr>"
            for i, (lbl, w) in enumerate(zip(cols_l, weights))
        ])

        st.markdown(f"""
        <div class="soft-card" style="padding:1.75rem 2rem;min-height:420px;">
            <div style="text-align:center;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid #E2ECF5;">
                <h3 style="color:#243B53;font-weight:700;font-size:1.1rem;margin:0 0 0.25rem;">
                    Laporan Analisis SPK Sunja Hana
                </h3>
                <p style="color:#627D98;font-size:0.83rem;margin:0;">
                    Periode: {period}
                </p>
                <p style="color:#829AB1;font-size:0.76rem;margin:0.2rem 0 0;">
                    ID Analisis: {aid} &nbsp;•&nbsp; Dicetak: {datetime.now().strftime('%d %B %Y')}
                </p>
            </div>

            <p style="font-weight:600;color:#243B53;font-size:0.88rem;margin-bottom:0.4rem;">
                Peringkat Prioritas Kategori
            </p>
            <div style="overflow-x:auto;margin-bottom:1.25rem;">
                <table style="width:100%;border-collapse:collapse;font-size:0.82rem;border:1px solid #E2ECF5;">
                    <thead>
                        <tr style="background:#EAF2FB;color:#243B53;">
                            <th style="padding:0.5rem 0.6rem;text-align:center;">Rank</th>
                            <th style="padding:0.5rem 0.6rem;text-align:left;">Kategori</th>
                            <th style="padding:0.5rem 0.6rem;text-align:center;">Vi</th>
                        </tr>
                    </thead>
                    <tbody>{rank_rows}</tbody>
                </table>
            </div>

            <p style="font-weight:600;color:#243B53;font-size:0.88rem;margin-bottom:0.4rem;">
                Bobot Kriteria (CRITIC)
            </p>
            <div style="overflow-x:auto;">
                <table style="width:100%;border-collapse:collapse;font-size:0.82rem;border:1px solid #E2ECF5;">
                    <thead>
                        <tr style="background:#EAF2FB;color:#243B53;">
                            <th style="padding:0.5rem 0.6rem;text-align:left;">Kriteria</th>
                            <th style="padding:0.5rem 0.6rem;text-align:center;">Bobot</th>
                        </tr>
                    </thead>
                    <tbody>{w_rows}</tbody>
                </table>
            </div>
        </div>
        """, unsafe_allow_html=True)
