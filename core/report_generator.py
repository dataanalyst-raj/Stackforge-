"""
StackForge - PDF Report Generator
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os


def generate_pdf_report(results: dict, output_path: str) -> str:
    """
    Generate a professional PDF design report.
    Returns the path of the generated file.
    """
    inputs = results.get("inputs", {})
    geometry = results.get("geometry", {})
    summary = results.get("summary", {})
    weights = results.get("weights", {}).get("summary", {})
    dynamic = results.get("dynamic", {})
    stress = results.get("stress", [])
    flanges = results.get("flanges", [])
    base = results.get("base", {})
    wind = results.get("wind", {})

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=18*mm,
        leftMargin=18*mm,
        topMargin=15*mm,
        bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#1e3a5f")
    )
    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=6,
        textColor=colors.HexColor("#1e3a5f")
    )
    normal = ParagraphStyle(
        "NormalStyle",
        parent=styles["Normal"],
        fontSize=9,
        leading=12
    )
    small = ParagraphStyle(
        "SmallStyle",
        parent=styles["Normal"],
        fontSize=8,
        leading=10
    )

    story = []

    # ---------- Title ----------
    story.append(Paragraph("STACKFORGE", title_style))
    story.append(Paragraph("Steel Chimney Design Report", ParagraphStyle(
        "Sub", parent=styles["Normal"], fontSize=11, alignment=TA_CENTER, spaceAfter=4
    )))
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d-%b-%Y %H:%M')}",
        ParagraphStyle("Date", parent=small, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 4*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1e3a5f")))
    story.append(Spacer(1, 4*mm))

    # ---------- Project Info ----------
    story.append(Paragraph("1. Project Information", heading_style))
    proj_data = [
        ["Project Name", inputs.get("project_name", "-"), "Client", inputs.get("client_name", "-")],
        ["Location", inputs.get("location", "-"), "Designed By", inputs.get("designed_by", "-")],
        ["Date", datetime.now().strftime("%d-%b-%Y"), "Checked By", inputs.get("checked_by", "-")],
    ]
    t = Table(proj_data, colWidths=[35*mm, 50*mm, 30*mm, 50*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef5")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e8eef5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)

    # ---------- Geometry ----------
    story.append(Paragraph("2. Geometry", heading_style))
    geo_data = [
        ["Total Height", f"{geometry.get('total_height', 0):.2f} m",
         "Flare Height", f"{geometry.get('flare_height', 0):.2f} m"],
        ["Top OD", f"{geometry.get('top_od', 0):.1f} mm",
         "Bottom OD", f"{geometry.get('bottom_od', 0):.1f} mm"],
        ["Number of Zones", str(len(geometry.get("zones", []))),
         "Lined / Unlined", "Lined" if inputs.get("is_lined") else "Unlined"],
    ]
    t = Table(geo_data, colWidths=[35*mm, 50*mm, 35*mm, 45*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef5")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e8eef5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)

    # Zone table
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("Shell Zones", ParagraphStyle("H3", parent=normal, fontName="Helvetica-Bold")))
    zone_header = ["Zone", "Portion", "Length (m)", "Top OD", "Bottom OD", "Thk (mm)"]
    zone_rows = [zone_header]
    thicknesses = results.get("thicknesses", [])
    for i, z in enumerate(geometry.get("zones", [])):
        thk = thicknesses[i]["practical_thickness"] if i < len(thicknesses) else "-"
        zone_rows.append([
            str(z["zone_no"]),
            z["portion"],
            f"{z['length']:.2f}",
            f"{z['top_od']:.0f}",
            f"{z['bottom_od']:.0f}",
            f"{thk:.0f}" if isinstance(thk, (int, float)) else str(thk)
        ])
    t = Table(zone_rows, colWidths=[18*mm, 28*mm, 28*mm, 28*mm, 28*mm, 25*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
    ]))
    story.append(t)

    # ---------- Dynamic & Loads ----------
    story.append(Paragraph("3. Dynamic Properties & Loads", heading_style))
    across = dynamic.get("across_wind", {})
    dyn_data = [
        ["Natural Frequency", f"{summary.get('natural_frequency', 0):.4f} Hz",
         "Time Period", f"{summary.get('period', 0):.4f} s"],
        ["Critical Velocity (Vcr)", f"{across.get('Vcr', 0):.2f} m/s",
         "Strakes Required", "Yes" if across.get("strakes_required") else "No"],
        ["Total Weight", f"{summary.get('total_weight', 0):.0f} kg",
         "Base Moment", f"{summary.get('base_moment', 0):.0f} kg-m"],
        ["Base Shear", f"{summary.get('base_shear', 0):.0f} kg",
         "Max Utilization", f"{summary.get('max_utilization', 0):.1f} %"],
    ]
    t = Table(dyn_data, colWidths=[40*mm, 40*mm, 40*mm, 35*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef5")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e8eef5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)

    # ---------- Shell Stress ----------
    story.append(Paragraph("4. Shell Stress Analysis", heading_style))
    stress_header = ["Zone", "Axial (kg)", "Moment (kg-m)", "σc", "σb", "Total", "Allow", "Status"]
    stress_rows = [stress_header]
    for s in stress:
        stress_rows.append([
            str(s.get("zone_no", "")),
            f"{s.get('axial_force', 0):.0f}",
            f"{s.get('moment', 0):.0f}",
            f"{s.get('sigma_c', 0):.1f}",
            f"{s.get('sigma_b', 0):.1f}",
            f"{s.get('sigma_total', 0):.1f}",
            f"{s.get('sigma_allow', 0):.1f}",
            s.get("status", "")
        ])
    t = Table(stress_rows, colWidths=[15*mm, 25*mm, 28*mm, 20*mm, 20*mm, 20*mm, 22*mm, 18*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
    ]))
    story.append(t)

    # ---------- Flanges ----------
    story.append(Paragraph("5. Flange Design", heading_style))
    fl_header = ["Sec", "Flange OD", "Thk", "Bolt", "Nos", "PCD", "Force (kg)", "Status"]
    fl_rows = [fl_header]
    for f in flanges:
        fl_rows.append([
            str(f.get("section", "")),
            f"{f.get('flange_od', 0):.0f}",
            f"{f.get('thickness', 0):.0f}",
            f.get("bolt_size", ""),
            str(f.get("num_bolts", "")),
            f"{f.get('PCD', 0):.0f}",
            f"{f.get('bolt_force', 0):.0f}",
            f.get("status", "")
        ])
    t = Table(fl_rows, colWidths=[15*mm, 25*mm, 18*mm, 18*mm, 15*mm, 25*mm, 28*mm, 20*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f7fa")]),
    ]))
    story.append(t)

    # ---------- Base Chair ----------
    story.append(Paragraph("6. Base Chair Design", heading_style))
    bolts = base.get("bolts", {})
    base_data = [
        ["Base OD", f"{base.get('base_od', 0):.0f} mm",
         "Bolt Circle", f"{bolts.get('bolt_circle', 0):.0f} mm"],
        ["Number of Bolts", str(bolts.get("num_bolts", "-")),
         "Bolt Size", bolts.get("bolt_size", "-")],
        ["Bolt Force", f"{bolts.get('bolt_force', 0):.0f} kg",
         "Base Plate Thk", f"{base.get('base_plate', {}).get('t_practical_mm', 0):.0f} mm"],
        ["Compression Plate", f"{base.get('compression_plate_thk', 0):.0f} mm",
         "Gusset Status", base.get("gusset", {}).get("status", "-")],
    ]
    t = Table(base_data, colWidths=[40*mm, 40*mm, 40*mm, 35*mm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e8eef5")),
        ("BACKGROUND", (2, 0), (2, -1), colors.HexColor("#e8eef5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t)

    # ---------- Footer note ----------
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "This report is generated by StackForge – Steel Chimney Design Software. "
        "Design is based on IS 6533, IS 875 (Part 3) and IS 1893. "
        "Results should be reviewed by a qualified structural engineer before use.",
        ParagraphStyle("Footer", parent=small, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    return output_path
