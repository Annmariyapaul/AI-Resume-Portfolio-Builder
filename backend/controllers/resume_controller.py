"""
controllers/resume_controller.py — Resume generation & management endpoints.
"""

import os
from flask import Blueprint, request, send_file
from services.resume_service    import ResumeService
from utils.validators           import validate_required_fields
from utils.response_helpers     import success, error
from utils.logger               import get_logger

logger = get_logger(__name__)

resume_bp = Blueprint('resume', __name__)
svc       = ResumeService()


@resume_bp.route('/generate', methods=['POST'])
def generate():
    """
    POST /api/resume/generate
    Body (JSON): { user_id, name, title, email, ... raw_input (free text) }
    Returns: { resume_data (structured), doc_id }
    """
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['user_id', 'raw_input'])
    if err:
        return error(err, 400)

    try:
        result = svc.generate(body)
        return success(result)
    except Exception as exc:
        logger.exception("Error in resume generation: %s", exc)
        return error(str(exc), 500)


@resume_bp.route('/enhance', methods=['POST'])
def enhance():
    """
    POST /api/resume/enhance
    Body: { doc_id, section, content }
    Returns: { enhanced_content }
    """
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['doc_id', 'section', 'content'])
    if err:
        return error(err, 400)

    try:
        result = svc.enhance_section(body)
        return success(result)
    except Exception as exc:
        logger.exception("Error in resume enhancement: %s", exc)
        return error(str(exc), 500)


@resume_bp.route('/download/<doc_id>', methods=['GET'])
def download(doc_id):
    """GET /api/resume/download/<doc_id> — Stream the generated PDF."""
    try:
        path = svc.get_pdf_path(doc_id)
        if not path or not os.path.exists(path):
            return error('PDF not found. Generate the resume first.', 404)
        return send_file(path, as_attachment=True,
                         download_name='resume.pdf', mimetype='application/pdf')
    except Exception as exc:
        logger.exception("Error downloading resume: %s", exc)
        return error(str(exc), 500)


@resume_bp.route('/save', methods=['POST'])
def save():
    """POST /api/resume/save — Persist resume data to Firestore."""
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['user_id', 'resume_data'])
    if err:
        return error(err, 400)

    try:
        doc_id = svc.save(body['user_id'], body['resume_data'])
        return success({'doc_id': doc_id})
    except Exception as exc:
        logger.exception("Error saving resume: %s", exc)
        return error(str(exc), 500)


@resume_bp.route('/list/<user_id>', methods=['GET'])
def list_resumes(user_id):
    """GET /api/resume/list/<user_id> — Fetch all resumes for a user."""
    try:
        resumes = svc.get_all(user_id)
        return success({'resumes': resumes})
    except Exception as exc:
        logger.exception("Error listing resumes: %s", exc)
        return error(str(exc), 500)


@resume_bp.route('/<doc_id>', methods=['DELETE'])
def delete(doc_id):
    """DELETE /api/resume/<doc_id>"""
    try:
        svc.delete(doc_id)
        return success({'message': 'Resume deleted.'})
    except Exception as exc:
        logger.exception("Error deleting resume: %s", exc)
        return error(str(exc), 500)
