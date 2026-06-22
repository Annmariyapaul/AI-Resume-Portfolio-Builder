"""
services/resume_service.py — Business logic for resume generation.
"""

import os
import json
from datetime import datetime
from flask import current_app
from gemini_api       import generate_json, generate_text
from firebase_config  import save_document, get_document, get_user_documents, delete_document
from pdf_generator    import generate_resume_pdf
from utils.logger     import get_logger

logger = get_logger(__name__)


class ResumeService:

    # ── AI Generation ─────────────────────────────────────────────────────────

    def generate(self, data: dict) -> dict:
        """
        Given raw user input (free text + any structured fields),
        call Gemini to produce a fully structured resume, generate the PDF,
        and persist to Firestore.
        """
        logger.info(f"Generating resume for user_id={data.get('user_id')}")
        
        try:
            prompt = self._build_prompt(data)
            logger.info("Built prompt, calling Gemini API...")
            raw    = generate_json(prompt, temperature=0.1, max_tokens=8192)
            logger.info(f"Gemini API response length: {len(raw)}")
        except Exception as exc:
            logger.error(f"Gemini API call failed: {exc}")
            raise RuntimeError(f"AI generation failed: {exc}") from exc

        try:

            print("\n========== GEMINI RAW RESPONSE ==========\n")
            print(raw)
            print("\n=========================================\n")


            resume_data = json.loads(raw)
            logger.info(f"Successfully parsed JSON response with keys: {list(resume_data.keys())}")
        except json.JSONDecodeError as jex:
            logger.warning(f"Initial JSON parse failed, attempting fallback extraction: {jex}")
            # Fallback: try to extract JSON substring
            try:
                start = raw.find('{')
                end   = raw.rfind('}') + 1
                if start >= 0 and end > start:
                    resume_data = json.loads(raw[start:end])
                    logger.info("Fallback JSON extraction succeeded")
                else:
                    raise jex
            except Exception as e2:
                logger.error(f"Fallback JSON extraction also failed: {e2}")
                raise RuntimeError(f"Could not parse AI response as JSON: {e2}") from e2

        resume_data['user_id']    = data['user_id']
        resume_data['created_at'] = datetime.utcnow().isoformat()

        # Persist to Firestore
        try:
            logger.info("Saving resume data to Firestore...")
            doc_id = save_document('resumes', resume_data)
            logger.info(f"Resume document created with ID: {doc_id}")
        except Exception as exc:
            logger.error(f"Failed to save resume document: {exc}")
            raise RuntimeError(f"Database save failed: {exc}") from exc

        # Generate PDF
        try:
            logger.info("Generating PDF...")
            pdf_path = self._make_pdf(resume_data, doc_id)
            logger.info(f"PDF generated at: {pdf_path}")
        except Exception as exc:
            logger.error(f"PDF generation failed: {exc}")
            raise RuntimeError(f"PDF generation failed: {exc}") from exc

        # Save PDF path into document
        try:
            resume_data['pdf_path'] = pdf_path
            save_document('resumes', resume_data, doc_id)
            logger.info(f"Updated resume document with PDF path")
        except Exception as exc:
            logger.error(f"Failed to update resume with PDF path: {exc}")
            # Don't fail here, PDF still exists

        return {
            'doc_id':      doc_id,
            'resume_data': resume_data,
            'pdf_path':    pdf_path,
        }

    def enhance_section(self, data: dict) -> dict:
        """AI-enhance a specific resume section."""
        prompt = (
            f"Improve the following resume {data['section']} section "
            f"to be more impactful, concise, and ATS-friendly.\n\n"
            f"Current content:\n{data['content']}\n\n"
            "Return only the improved text."
        )
        enhanced = generate_text(prompt, temperature=0.6)
        return {'enhanced_content': enhanced}

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def save(self, user_id: str, resume_data: dict) -> str:
        resume_data['user_id']    = user_id
        resume_data['updated_at'] = datetime.utcnow().isoformat()
        return save_document('resumes', resume_data)

    def get_all(self, user_id: str) -> list:
        return get_user_documents('resumes', user_id)

    def delete(self, doc_id: str):
        delete_document('resumes', doc_id)

    def get_pdf_path(self, doc_id: str) -> str | None:
        doc = get_document('resumes', doc_id)
        return doc.get('pdf_path') if doc else None

    # ── Internals ─────────────────────────────────────────────────────────────

    def _build_prompt(self, data: dict) -> str:
        return f"""
You are an expert resume writer and career coach.
Convert the following user information into a professional, ATS-optimised resume.
Return ONLY valid JSON.
Do not use markdown.
Do not include ```json or ``` delimiters.

Return a JSON object using this schema.
Only include sections for which information is available.
Do not invent universities, companies, projects, certifications, dates, GPA, skills, or achievements.

If a section has no information, return an empty list [].
Never return objects whose fields are all empty.

Use empty strings "" only for missing optional fields inside an existing object.
Do not use placeholders such as [University Name], N/A, Unknown, or dummy values.

Only include skill categories that contain at least one skill.
Do not create empty categories.

User input:
{data.get('raw_input', '')}

Additional structured data (if any):
Name:     {data.get('name', '')}
Title:    {data.get('title', '')}
Email:    {data.get('email', '')}
Phone:    {data.get('phone', '')}
Location: {data.get('location', '')}
LinkedIn: {data.get('linkedin', '')}
GitHub:   {data.get('github', '')}



Never return lists containing empty objects.

Examples:
No education → "education": []
No projects → "projects": []
No certifications → "certifications": []

Only include skill categories that contain at least one item.

Example:

{{
  "Languages": ["C", "Java", "Python"]
}}

Do NOT return:

{{
  "Languages": ["C", "Java", "Python"],
  "Frameworks": [],
  "Tools": []
}}

Return a JSON object with this exact schema:
{{
  "name": "",
  "title": "",
  "email": "",
  "phone": "",
  "location": "",
  "linkedin": "",
  "github": "",
  "summary": "2–3 sentence professional summary",
  "experience": [
    {{
      "role": "",
      "company": "",
      "duration": "MMM YYYY – MMM YYYY",
      "location": "",
      "bullets": ["achievement-focused bullet", "..."]
    }}
  ],
  "education": [
    {{
      "degree": "",
      "institution": "",
      "duration": "YYYY-YYYY",
      "gpa": ""
    }}
  ],
  "skills": {{
    "Languages": ["Python", "..."],
    "Frameworks": ["Flask", "..."],
    "Tools": ["Git", "..."]
  }},
  "projects": [
    {{
      "name": "",
      "description": "",
      "tech": ["..."],
      "link": ""
    }}
  ],
  "certifications": [
    {{ "name": "" }}
  ]
}}

Make bullet points start with strong action verbs and include metrics where possible.
"""

    def _make_pdf(self, resume_data: dict, doc_id: str) -> str:
        out_dir  = current_app.config['GENERATED_FILES_DIR']
        filename = f"resume_{doc_id}.pdf"
        path     = os.path.join(out_dir, filename)
        generate_resume_pdf(resume_data, path)
        return path
