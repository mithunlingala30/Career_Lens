"""Professional PDF evaluation report (ReportLab)."""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

NAVY, BLUE, VIOLET, PINK, TEAL = (colors.HexColor(c) for c in ("#14204a", "#2f6bff", "#7a3cff", "#ff3d95", "#00a98f"))


def build_report(ev, profile, recs) -> bytes:
    d = ev["details"]
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title="CareerLens Evaluation Report")
    ss = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=ss["Title"], textColor=NAVY, fontSize=22, alignment=0, spaceAfter=2)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=VIOLET, fontSize=13, spaceBefore=12, spaceAfter=4)
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=13, textColor=NAVY)
    small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.HexColor("#5b6892"))
    S = []
    S.append(Paragraph("CareerLens Evaluation Report", h1))
    S.append(Paragraph(f"Generated {datetime.now():%d %b %Y, %H:%M} &nbsp;|&nbsp; Target role: <b>{d.get('job_title', '')}</b> at {d.get('company', '')}", small))
    S.append(Spacer(1, 8))

    def card(label, value, color):
        t = Table([[Paragraph(f"<font color='white' size=19><b>{value}</b></font>", body)], [Paragraph(f"<font color='white' size=8>{label}</font>", body)]], colWidths=[40 * mm])
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), color), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 6),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        return t
    readiness = recs[0]["readiness"] if recs else None
    S.append(Table([[card("Resume score /100", f"{ev['resume_score']:.0f}", BLUE), card("Job compatibility", f"{ev['compatibility']:.0f}%", VIOLET),
                     card("Career readiness", f"{readiness:.0f}%" if readiness is not None else "n/a", PINK),
                     card("Percentile", f"{d.get('gaussian', {}).get('percentile', 0):.0f}", TEAL)]], colWidths=[43 * mm] * 4))

    S.append(Paragraph("Candidate details", h2))
    rows = [["Name", profile["full_name"] or "-"], ["Email", profile["email"] or "-"], ["Phone", profile["phone"] or "-"],
            ["Location", profile["location"] or "-"], ["Experience", f"{profile['total_experience_years']} years"]]
    t = Table(rows, colWidths=[30 * mm, 140 * mm])
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9), ("TEXTCOLOR", (0, 0), (0, -1), VIOLET), ("TEXTCOLOR", (1, 0), (1, -1), NAVY),
                           ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#d6dcee"))]))
    S.append(t)

    S.append(Paragraph("Score breakdown (job compatibility)", h2))
    rows = [["Component", "Score", "Weight", "Contribution"]] + [[c["name"], f"{c['score']}%", f"{int(c['weight'] * 100)}%", f"{c['contribution']}"] for c in d.get("score_components", [])]
    t = Table(rows, colWidths=[75 * mm, 30 * mm, 30 * mm, 35 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), VIOLET), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTSIZE", (0, 0), (-1, -1), 9),
                           ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef2fb")])]))
    S.append(t)

    S.append(Paragraph("Skills", h2))
    matched = ", ".join(f"{m['skill']}" for m in d.get("matched_skills", [])) or "None"
    missing = ", ".join(f"{m['skill']}{' (mandatory)' if m.get('mandatory') else ''}" for m in d.get("missing_skills", [])) or "None - all required skills present"
    S.append(Paragraph(f"<font color='#00a98f'><b>Matched skills:</b></font> {matched}", body))
    S.append(Spacer(1, 3))
    S.append(Paragraph(f"<font color='#ff3d95'><b>Missing skills:</b></font> {missing}", body))

    S.append(Paragraph("Education and experience analysis", h2))
    em, xm = d.get("education_match", {}), d.get("experience_match", {})
    S.append(Paragraph(f"Education: required <b>{em.get('required_label')}</b>, candidate holds <b>{em.get('candidate_label')}</b> - "
                       f"{'requirement met' if em.get('met') else 'below requirement'} (score {em.get('score')}%).", body))
    S.append(Paragraph(f"Experience: required <b>{xm.get('required_years')}</b> years, candidate has <b>{xm.get('candidate_years')}</b> years (score {xm.get('score')}%).", body))

    g, b, c, sv = d.get("gaussian", {}), d.get("bayes", {}), d.get("conditional", {}), d.get("svd", {})
    S.append(Paragraph("Statistical insights", h2))
    S.append(Paragraph(f"Bayes posterior suitability <b>{b.get('posterior', 0) * 100:.1f}%</b> (prior {b.get('prior', 0) * 100:.0f}%, Bayes factor {b.get('bayes_factor', 0):.1f}). "
                       f"Empirical conditional probability P(suitable | evidence) = <b>{c.get('p_conditional', 0) * 100:.1f}%</b>. "
                       f"Latent (SVD) fit <b>{sv.get('similarity', 0) * 100:.1f}%</b>. "
                       f"Resume score z = <b>{g.get('z_score', 0):.2f}</b> against a cohort mean of {g.get('mean', 0):.1f} (sd {g.get('std', 0):.1f}) - {g.get('band', '')}.", body))

    S.append(Paragraph("Career recommendations", h2))
    for r in recs[:4]:
        mk = r["progression"].get("markov", {})
        S.append(Paragraph(f"<b>{r['category']}</b> - suitability {r['suitability']:.0f}%, readiness {r['readiness']:.0f}% "
                           f"(stage: {mk.get('current_state_name', '')}).", body))
        miss = ", ".join(m["skill"] for m in r["missing_skills"][:6]) or "none"
        S.append(Paragraph(f"&nbsp;&nbsp;Skills to build: {miss}", small))
    S.append(Paragraph("Skill development suggestions", h2))
    tips = (recs[0]["progression"].get("development_suggestions", []) if recs else []) or [m["skill"] for m in d.get("missing_skills", [])[:5]]
    for tip in tips[:6]:
        S.append(Paragraph(f"&bull; {tip}", body))
    S.append(Spacer(1, 10))
    S.append(Paragraph("Scores are model estimates based on the resume text and the job catalogue; probabilities rely on stated assumptions "
                       "(see README) and should support, not replace, human judgement.", small))
    doc.build(S)
    return buf.getvalue()
