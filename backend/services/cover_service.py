"""
services/cover_service.py — Business logic for cover letter generation.
"""

import os
import json
from datetime import datetime
from flask import current_app
from gemini_api       import generate_text
from firebase_config  import (
    save_document,
    get_document, 
    get_user_documents,
    update_document
)
from pdf_generator    import generate_cover_letter_pdf
from utils.logger     import get_logger

logger = get_logger(__name__)


class CoverLetterService:

    def generate(self, data: dict) -> dict:
        prompt = self._build_prompt(data)
        body   = generate_text(prompt, temperature=0.7, max_tokens=1500)

        cover_data = {
            'user_id':        data['user_id'],
            'name':           data.get('name', ''),
            'email':          data.get('email', ''),
            'phone':          data.get('phone', ''),
            'recipient_name': data.get('recipient_name', 'Hiring Manager'),
            'recipient_title':data.get('recipient_title', ''),
            'company':        data['company'],
            'job_title':      data['job_title'],
            'body':           body,
            'closing':        'Sincerely',
            'date':           datetime.now().strftime('%B %d, %Y'),
            'created_at':     datetime.utcnow().isoformat(),
        }

        doc_id   = save_document('cover_letters', cover_data)
        pdf_path = self._make_pdf(cover_data, doc_id)
        cover_data['pdf_path'] = pdf_path

        update_document(
        'cover_letters',
        doc_id,
        {'pdf_path': pdf_path}
        )

        return {'doc_id': doc_id, 'cover_data': cover_data}

    def save(self, user_id: str, cover_data: dict) -> str:
        cover_data['user_id']    = user_id
        cover_data['updated_at'] = datetime.utcnow().isoformat()
        return save_document('cover_letters', cover_data)

    def get_all(self, user_id: str) -> list:
        return get_user_documents('cover_letters', user_id)

    def get_pdf_path(self, doc_id: str) -> str | None:
        doc = get_document('cover_letters', doc_id)
        return doc.get('pdf_path') if doc else None

    # ── Internals ─────────────────────────────────────────────────────────────

    def _build_prompt(self, data: dict) -> str:
        resume_context = ''
        if data.get('resume_summary'):
            resume_context = f"\nApplicant's resume summary:\n{data['resume_summary']}"

        return f"""
Write a compelling, professional cover letter for the following job application.

Job title:       {data['job_title']}
Company:         {data['company']}
Job description: {data.get('job_description', 'Not provided')}
{resume_context}

Guidelines:
- 3–4 paragraphs: hook, why this role/company, key achievements, call to action.
- Tone: confident, enthusiastic, professional — not sycophantic.
- Tailor language to the job description keywords.
- Do NOT include salutation or closing — return body paragraphs only.
- Separate paragraphs with a blank line.
- Do not invent experience, skills, projects, or achievements that are not provided.
- Use only information from the job description and resume summary.
"""

    def _make_pdf(self, cover_data: dict, doc_id: str) -> str:
        out_dir  = current_app.config['GENERATED_FILES_DIR']
        filename = f"cover_letter_{doc_id}.pdf"
        path     = os.path.join(out_dir, filename)
        generate_cover_letter_pdf(cover_data, path)
        return path
