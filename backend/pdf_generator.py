"""
pdf_generator.py — PDF generation using ReportLab.
Generates professionally styled Resume and Cover Letter PDFs.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Palette ──────────────────────────────────────────────────────────────────
DARK    = colors.HexColor('#1a1a2e')
ACCENT  = colors.HexColor('#4f46e5')
LIGHT   = colors.HexColor('#f8f8ff')
GREY    = colors.HexColor('#6b7280')
WHITE   = colors.white


def _base_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle('ResumeName',
        fontName='Helvetica-Bold', fontSize=22, leading=28, textColor=DARK,
        spaceAfter=2, alignment=TA_LEFT))

    styles.add(ParagraphStyle('ResumeTitle',
        fontName='Helvetica', fontSize=12, leading=14, textColor=ACCENT,
        spaceAfter=4, alignment=TA_LEFT))

    styles.add(ParagraphStyle('ContactLine',
        fontName='Helvetica', fontSize=9, textColor=GREY,
        spaceAfter=12, alignment=TA_LEFT))

    styles.add(ParagraphStyle('SectionHeader',
        fontName='Helvetica-Bold', fontSize=11, textColor=ACCENT,
        spaceBefore=14, spaceAfter=4))

    styles.add(ParagraphStyle('JobTitle',
        fontName='Helvetica-Bold', fontSize=10, textColor=DARK,
        spaceAfter=1))

    styles.add(ParagraphStyle('JobMeta',
        fontName='Helvetica-Oblique', fontSize=9, textColor=GREY,
        spaceAfter=4))

    styles.add(ParagraphStyle('BodyText2',
        fontName='Helvetica', fontSize=9.5, textColor=DARK,
        leading=14, alignment=TA_JUSTIFY, spaceAfter=4))

    styles.add(ParagraphStyle('BulletItem',
        fontName='Helvetica', fontSize=9.5, textColor=DARK,
        leading=13, leftIndent=12, bulletIndent=4, spaceAfter=2))

    styles.add(ParagraphStyle('SkillTag',
        fontName='Helvetica', fontSize=9, textColor=DARK,
        spaceAfter=4))

    # Cover-letter specific
    styles.add(ParagraphStyle('CoverBody',
        fontName='Helvetica', fontSize=10.5, textColor=DARK,
        leading=16, alignment=TA_JUSTIFY, spaceAfter=10))

    styles.add(ParagraphStyle('CoverHeading',
        fontName='Helvetica-Bold', fontSize=14, textColor=DARK,
        spaceAfter=4))

    return styles


def _divider():
    return HRFlowable(width='100%', thickness=0.5,
                      color=ACCENT, spaceAfter=6, spaceBefore=2)


# ── Public API ────────────────────────────────────────────────────────────────

def generate_resume_pdf(data: dict, output_path: str) -> str:
    """
    Build a resume PDF from *data* dict and write it to *output_path*.

    Expected *data* keys (all optional except 'name'):
        name, title, email, phone, location, linkedin, github,
        summary, experience (list), education (list),
        skills (list), projects (list), certifications (list)

    Returns the absolute file path.
    """
    try:
        logger.info(f"Generating resume PDF to: {output_path}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            topMargin=1.8*cm, bottomMargin=1.8*cm,
            leftMargin=2*cm, rightMargin=2*cm
        )
        styles = _base_styles()
        story  = []

        # ── Header ────────────────────────────────────────────────────────────────
        story.append(Paragraph(data.get('name', 'Your Name'), styles['ResumeName']))
        if data.get('title'):
            story.append(Paragraph(data['title'], styles['ResumeTitle']))

        story.append(Spacer(1, 8))

        contact_parts = [x for x in [
            data.get('email'), data.get('phone'),
            data.get('location'), data.get('linkedin'), data.get('github')
        ] if x]
        if contact_parts:
            story.append(Paragraph(' · '.join(contact_parts), styles['ContactLine']))

        story.append(_divider())

        # ── Summary ───────────────────────────────────────────────────────────────
        if data.get('summary'):
            story.append(Paragraph('PROFESSIONAL SUMMARY', styles['SectionHeader']))
            story.append(_divider())
            story.append(Paragraph(data['summary'], styles['BodyText2']))

        # ── Experience ────────────────────────────────────────────────────────────
        if data.get('experience'):
            story.append(Paragraph('EXPERIENCE', styles['SectionHeader']))
            story.append(_divider())
            for exp in data['experience']:
                story.append(Paragraph(
                    f"{exp.get('role', '')} — {exp.get('company', '')}",
                    styles['JobTitle']))
               
                duration = exp.get('duration', '')
                location = exp.get('location', '')

                meta = " | ".join(
                    item for item in [duration, location]
                    if item
                )

                if meta:
                    story.append(
                        Paragraph(meta, styles['JobMeta'])
                    )

                for bullet in exp.get('bullets', []):
                    story.append(Paragraph(f'• {bullet}', styles['BulletItem']))
                story.append(Spacer(1, 4))

        
        # ── Education ────────────────────────────────────────────────────────────
        if data.get('education'):
            valid_education = [
                edu for edu in data['education']
                if any(edu.values())
            ]

            if valid_education:
                story.append(Paragraph('EDUCATION', styles['SectionHeader']))
                story.append(_divider())

                for edu in valid_education:
                    story.append(
                        Paragraph(
                            f"{edu.get('degree','')} — {edu.get('institution','')}",
                            styles['JobTitle']
                        )
                    )

                    duration = edu.get('duration', '')
                    gpa = edu.get('gpa', '')
                    
                    # Clean up GPA field (remove any existing CGPA prefix)
                    if gpa:
                        gpa = gpa.replace('CGPA:', '').replace('GPA:', '').strip()

                    meta_parts = [duration, f"CGPA: {gpa}" if gpa else '']
                    meta = ' | '.join(p for p in meta_parts if p)

                    if meta:
                        story.append(
                            Paragraph(
                                meta, 
                                styles['JobMeta']
                            )
                        )

        # ── Skills ────────────────────────────────────────────────────────────────
        if data.get('skills'):
            story.append(Paragraph('SKILLS', styles['SectionHeader']))
            story.append(_divider())
            
            if isinstance(data['skills'], dict):
                for category, skill_list in data['skills'].items():
                    if skill_list:      # Skip empty categories
                        label = f"<b>{category}:</b> "
                        items = ', '.join(skill_list)

                        story.append(
                            Paragraph(
                                f"{label}{items}",
                                styles['SkillTag']
                            )
                        )

            else:
                story.append(
                    Paragraph(
                        ', '.join(data['skills']),
                        styles['SkillTag']
                    )
                )
            

        
        # ── Projects ─────────────────────────────────────────────────────────────
        valid_projects = [
            proj for proj in data.get('projects', [])
            if any(proj.values())
        ]

        if valid_projects:
            story.append(Paragraph('PROJECTS', styles['SectionHeader']))
            story.append(_divider())

            for proj in valid_projects:
                story.append(
                    Paragraph(
                        proj.get('name', ''),
                        styles['JobTitle']
                    )
                )

                if proj.get('description'):
                    story.append(
                        Paragraph(
                            proj['description'],
                            styles['BodyText2']
                        )
                    )

                if proj.get('tech'):
                    story.append(
                        Paragraph(
                            f"<i>Technologies: {', '.join(proj['tech'])}</i>",
                            styles['JobMeta']
                        )
                    )

             

        # ── Certifications ────────────────────────────────────────────────────────
        valid_certifications = [
            cert for cert in data.get('certifications', [])
            if cert.get('name')
        ]

        if valid_certifications:
            story.append(Paragraph('CERTIFICATIONS', styles['SectionHeader']))
            story.append(_divider())

            for cert in valid_certifications:
                story.append(
                    Paragraph(
                        f"• {cert['name']}",
                        styles['BulletItem']
                    )
                )    

        doc.build(story)
        logger.info(f"Resume PDF successfully built at {output_path}")
        return output_path
        
    except Exception as exc:
        logger.error(f"PDF generation failed: {exc}", exc_info=True)
        raise RuntimeError(f"Failed to generate PDF: {exc}") from exc


def generate_cover_letter_pdf(data: dict, output_path: str) -> str:
    """
    Build a cover-letter PDF from *data* dict.

    Expected keys:
        name, email, phone, date,
        recipient_name, recipient_title, company,
        body (plain text or list of paragraphs),
        closing (e.g. 'Sincerely')

    Returns the absolute file path.
    """
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=2.5*cm, bottomMargin=2.5*cm,
        leftMargin=2.5*cm, rightMargin=2.5*cm
    )
    styles = _base_styles()
    story  = []

    # Sender block
    story.append(Paragraph(data.get('name', ''), styles['CoverHeading']))
    contact_parts = [x for x in [data.get('email'), data.get('phone')] if x]
    story.append(Paragraph(' · '.join(contact_parts), styles['ContactLine']))
    story.append(Spacer(1, 6))

    # Date
    date_str = data.get('date', datetime.now().strftime('%B %d, %Y'))
    story.append(Paragraph(date_str, styles['CoverBody']))
    story.append(Spacer(1, 6))

    # Recipient
    if data.get('recipient_name'):
        story.append(Paragraph(data['recipient_name'], styles['CoverBody']))
    if data.get('recipient_title'):
        story.append(Paragraph(data['recipient_title'], styles['CoverBody']))
    if data.get('company'):
        story.append(Paragraph(data['company'], styles['CoverBody']))
    story.append(Spacer(1, 10))

    # Salutation
    salutation = f"Dear {data.get('recipient_name', 'Hiring Manager')},"
    story.append(Paragraph(salutation, styles['CoverBody']))

    # Body paragraphs
    body = data.get('body', '')
    paragraphs = body if isinstance(body, list) else body.split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), styles['CoverBody']))

    # Closing
    closing = data.get('closing', 'Sincerely')
    story.append(Spacer(1, 12))
    story.append(Paragraph(closing + ',', styles['CoverBody']))
    story.append(Spacer(1, 24))
    story.append(Paragraph(data.get('name', ''), styles['CoverBody']))

    doc.build(story)
    logger.info("Cover letter PDF saved → %s", output_path)
    return output_path
