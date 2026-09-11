from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_pdf():
    pdf_filename = "MARL_MEP_Routing_Report.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'H2Style',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1D4ED8'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        spaceAfter=6
    )

    # Title
    story.append(Paragraph("Automated MEP Layout Synthesis and Embodied Carbon Optimization Using Multi-Agent Reinforcement Learning and Direct CAD Integration", title_style))
    story.append(Spacer(1, 10))

    # Abstract
    story.append(Paragraph("Abstract", h2_style))
    abstract_text = (
        "<b>Context:</b> Traditional Mechanical, Electrical, and Plumbing (MEP) drafting relies on manual polyline routing, "
        "which is time-consuming and prone to EMC clearance errors.<br/>"
        "<b>Methodology:</b> We propose a Multi-Agent Reinforcement Learning (MARL) framework utilizing cooperative Q-learning "
        "agents to dynamically route power and low-voltage data circuits around architectural obstacles while maintaining strict EMC physical separation.<br/>"
        "<b>Results:</b> Synthesized spatial routes are exported via a clean data contract to AutoLISP, automatically generating 90° "
        "orthogonal polylines, standard engineering symbol blocks, and a dynamic schedule table tracking circuit length and embodied carbon (kg CO2e)."
    )
    story.append(Paragraph(abstract_text, body_style))
    story.append(Spacer(1, 10))

    # Architecture
    story.append(Paragraph("1. System Architecture & Formulations", h2_style))
    arch_text = (
        "<b>State Space:</b> S = [x_power, y_power, x_data, y_data]<br/>"
        "<b>Reward Function:</b> R_total = R_distance + R_bend + R_obstacle + R_EMC<br/>"
        "<b>Embodied Carbon Formula:</b> E_c = ∑ (L_i × EF_i)<br/>"
        "• Power Circuit (3x2.5mm² Cu): EF = 0.85 kg CO2e / m<br/>"
        "• Data Circuit (Cat6 UTP): EF = 0.18 kg CO2e / m"
    )
    story.append(Paragraph(arch_text, body_style))
    story.append(Spacer(1, 10))

    # Results Table
    story.append(Paragraph("2. Experimental Results Summary", h2_style))
    table_data = [
        ['Metric', 'Power Circuit (P1-RL)', 'Data Circuit (LV1-RL)', 'Combined System'],
        ['Circuit Type', '3-Drop Ring Main', 'Single Radial Outlet', 'Multi-Agent Network'],
        ['Conductor / Cable', '3x2.5 mm² Copper', 'Cat6 UTP', 'Mixed'],
        ['Routed Length (m)', '15.2 m', '11.6 m', '26.8 m'],
        ['Embodied Carbon', '12.92 kg CO2e', '2.09 kg CO2e', '15.01 kg CO2e'],
        ['EMC Violations', '0', '0', 'Passed'],
        ['Obstacle Collisions', '0', '0', 'Passed']
    ]

    t = Table(table_data, colWidths=[120, 130, 130, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F4F6')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
    ]))
    story.append(t)

    doc.build(story)
    print("✅ PDF successfully generated: MARL_MEP_Routing_Report.pdf")

if __name__ == "__main__":
    build_pdf()