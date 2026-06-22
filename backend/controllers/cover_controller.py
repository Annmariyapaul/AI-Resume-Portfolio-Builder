"""
controllers/cover_controller.py — Cover letter endpoints.
"""

import os
from flask import Blueprint, request, jsonify, send_file
from services.cover_service  import CoverLetterService
from utils.validators        import validate_required_fields
from utils.response_helpers  import success, error

cover_bp = Blueprint('cover', __name__)
svc      = CoverLetterService()


@cover_bp.route('/generate', methods=['POST'])
def generate():
    """
    POST /api/cover-letter/generate
    Body: { user_id, job_title, company, job_description, resume_doc_id (opt) }
    """
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['user_id', 'job_title', 'company'])
    if err:
        return error(err, 400)

    try:
        result = svc.generate(body)
        return success(result)
    except Exception as exc:
        return error(str(exc), 500)


@cover_bp.route('/download/<doc_id>', methods=['GET'])
def download(doc_id):
    """GET /api/cover-letter/download/<doc_id>"""
    try:
        path = svc.get_pdf_path(doc_id)
        if not path or not os.path.exists(path):
            return error('PDF not found.', 404)
        return send_file(path, as_attachment=True,
                         download_name='cover_letter.pdf',
                         mimetype='application/pdf')
    except Exception as exc:
        return error(str(exc), 500)


@cover_bp.route('/save', methods=['POST'])
def save():
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['user_id', 'cover_data'])
    if err:
        return error(err, 400)

    try:
        doc_id = svc.save(body['user_id'], body['cover_data'])
        return success({'doc_id': doc_id})
    except Exception as exc:
        return error(str(exc), 500)


@cover_bp.route('/list/<user_id>', methods=['GET'])
def list_covers(user_id):
    try:
        covers = svc.get_all(user_id)
        return success({'covers': covers})
    except Exception as exc:
        return error(str(exc), 500)
