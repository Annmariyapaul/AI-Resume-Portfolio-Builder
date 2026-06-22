"""
controllers/portfolio_controller.py — Portfolio generation endpoints.
"""

from flask import Blueprint, request
from services.portfolio_service import PortfolioService
from utils.validators           import validate_required_fields
from utils.response_helpers     import success, error

portfolio_bp = Blueprint('portfolio', __name__)
svc          = PortfolioService()


@portfolio_bp.route('/generate', methods=['POST'])
def generate():
    """
    POST /api/portfolio/generate
    Body: { user_id, name, title, bio, skills, projects, socials }
    Returns: { html_content, doc_id }
    """
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['user_id', 'name'])
    if err:
        return error(err, 400)

    try:
        result = svc.generate(body)
        return success(result)
    except Exception as exc:
        return error(str(exc), 500)


@portfolio_bp.route('/save', methods=['POST'])
def save():
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['user_id', 'portfolio_data'])
    if err:
        return error(err, 400)

    try:
        doc_id = svc.save(body['user_id'], body['portfolio_data'])
        return success({'doc_id': doc_id})
    except Exception as exc:
        return error(str(exc), 500)


@portfolio_bp.route('/list/<user_id>', methods=['GET'])
def list_portfolios(user_id):
    try:
        portfolios = svc.get_all(user_id)
        return success({'portfolios': portfolios})
    except Exception as exc:
        return error(str(exc), 500)


@portfolio_bp.route('/<doc_id>', methods=['DELETE'])
def delete(doc_id):
    try:
        svc.delete(doc_id)
        return success({'message': 'Portfolio deleted.'})
    except Exception as exc:
        return error(str(exc), 500)
