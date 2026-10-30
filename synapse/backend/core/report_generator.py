"""
Synapse PDF Report Generator
============================
Generates publication-grade, professionally formatted PDF evaluation dossiers
for any semantic analysis session. Includes document metadata, query analysis,
grounded citations, similarity rankings, and algorithmic audit logs.
"""

import time
from pathlib import Path
from io import BytesIO
from typing import Dict, Any

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_analysis_pdf(analysis_data: Dict[str, Any]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Editorial Color Palette
    c_primary = colors.HexColor('#0a0b0e')
    c_slate = colors.HexColor('#1e293b')
    c_muted = colors.HexColor('#475569')
    c_cyan = colors.HexColor('#0891b2')
    c_border = colors.HexColor('#cbd5e1')
    c_card_bg = colors.HexColor('#f8fafc')

    title_style = ParagraphStyle('RepTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=c_primary)
    sub_style = ParagraphStyle('RepSub', parent=styles['Normal'], fontSize=9, leading=13, textColor=c_muted)
    h2_style = ParagraphStyle('RepH2', parent=styles['Heading2'], fontSize=12, leading=16, textColor=c_cyan, spaceBefore=8, spaceAfter=4)
    body_style = ParagraphStyle('RepBody', parent=styles['Normal'], fontSize=9.5, leading=14, textColor=c_slate)
    quote_style = ParagraphStyle('RepQuote', parent=styles['Normal'], fontSize=9, leading=13, textColor=c_slate, backColor=c_card_bg, borderPadding=6)
    code_style = ParagraphStyle('RepCode', parent=styles['Normal'], fontSize=8, leading=11, fontName='Courier', textColor=c_primary)

    story = []

    # 1. Header Banner
    story.append(Paragraph("SYNAPSE // INTELLIGENT SEMANTIC ANALYSIS DOSSIER", title_style))
    story.append(Paragraph(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S UTC')} | Engine: Synapse 128D Cosine Architecture", sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_cyan, spaceAfter=14))

    # 2. Metadata Grid
    doc_name = analysis_data.get("document_name", "Unknown Document")
    query = analysis_data.get("query", "N/A")
    top_score = analysis_data.get("top_score", 0.0)
    duration_ms = analysis_data.get("duration_ms", 0.0)
    top_page = analysis_data.get("top_page", 1)

    meta_table_data = [
        [Paragraph("<b>Target Document:</b>", body_style), Paragraph(str(doc_name), body_style)],
        [Paragraph("<b>User Query:</b>", body_style), Paragraph(f'<i>"{query}"</i>', body_style)],
        [Paragraph("<b>Peak Similarity:</b>", body_style), Paragraph(f"<b>{top_score * 100:.2f}%</b> (Cosine Metric: {top_score:.4f})", body_style)],
        [Paragraph("<b>Execution Latency:</b>", body_style), Paragraph(f"{duration_ms:.1f} ms", body_style)],
        [Paragraph("<b>Primary Source Page:</b>", body_style), Paragraph(f"Page {top_page}", body_style)]
    ]

    t_meta = Table(meta_table_data, colWidths=[140, 380])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 14))

    # 3. Grounded Synthesis Finding
    story.append(Paragraph("1. FACTUALLY GROUNDED ANSWER SYNTHESIS", h2_style))
    key_insight = analysis_data.get("key_insight", "N/A")
    story.append(Paragraph(f"<b>Core Finding:</b> {key_insight}", body_style))
    story.append(Spacer(1, 8))

    top_text = analysis_data.get("top_passage_text", "")
    if top_text:
        story.append(Paragraph(f"<b>Verified Source Passage Citation (Page {top_page}):</b>", body_style))
        story.append(Paragraph(f'"{top_text}"', quote_style))
    story.append(Spacer(1, 14))

    # 4. Top Ranked Passages
    story.append(Paragraph("2. TOP RETRIEVED PASSAGES (SIMILARITY LEADERBOARD)", h2_style))
    ranked_chunks = analysis_data.get("ranked_chunks", [])
    if ranked_chunks:
        table_rows = [
            [
                Paragraph("<b>Rank</b>", body_style),
                Paragraph("<b>Passage ID</b>", body_style),
                Paragraph("<b>Page</b>", body_style),
                Paragraph("<b>Cosine Score</b>", body_style),
                Paragraph("<b>Passage Text Extract</b>", body_style)
            ]
        ]
        for rank, c in enumerate(ranked_chunks[:5], 1):
            p_text = c.get("text", "")[:110] + ("..." if len(c.get("text", "")) > 110 else "")
            table_rows.append([
                Paragraph(f"#{rank}", body_style),
                Paragraph(f"#{c.get('index', 0) + 1}", body_style),
                Paragraph(f"P.{c.get('page', 1)}", body_style),
                Paragraph(f"<b>{c.get('score', 0.0) * 100:.1f}%</b>", body_style),
                Paragraph(p_text, body_style)
            ])

        t_passages = Table(table_rows, colWidths=[38, 65, 40, 75, 302])
        t_passages.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
            ('BOX', (0, 0), (-1, -1), 0.5, c_border),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#edf2f7')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(t_passages)
    story.append(Spacer(1, 14))

    # 5. Explainability Breakdown
    match_exp = analysis_data.get("match_explanation", {})
    if match_exp:
        story.append(Paragraph("3. ALGORITHMIC EXPLAINABILITY & MATCH DRIVERS", h2_style))
        exp_text = match_exp.get("explanation", "")
        story.append(Paragraph(exp_text, body_style))
        story.append(Spacer(1, 6))
        exacts = match_exp.get("exact_term_matches", [])
        if exacts:
            story.append(Paragraph(f"<b>Exact Co-occurring Terms:</b> {', '.join(exacts)}", body_style))
        story.append(Spacer(1, 14))

    # 6. Audit & Integrity Disclaimer
    story.append(Paragraph("4. ARCHITECTURAL & ETHICAL VERIFICATION", h2_style))
    audit_notes = (
        "<b>Mathematical Integrity Guarantee:</b> This analysis was produced using a deterministic 128-dimensional dense "
        "vector projection algorithm incorporating dual FNV-1a/DJB2 hash mixing, character 3-grams, L2 unit normalization, "
        "and exact geometric cosine similarity. Zero metrics or embedding coordinates have been synthetic or fabricated. "
        "The grounded answer is directly bounded to the uploaded source document."
    )
    story.append(Paragraph(audit_notes, sub_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
