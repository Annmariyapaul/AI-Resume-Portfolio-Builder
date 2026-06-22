"""
controllers/user_controller.py — User profile & auth endpoints.
Authentication is delegated to Firebase on the frontend;
this controller just persists/retrieves profile data.
"""

from flask import Blueprint, request
from services.user_service  import UserService
from utils.validators       import validate_required_fields
from utils.response_helpers import success, error

user_bp = Blueprint('user', __name__)
svc     = UserService()


@user_bp.route('/profile', methods=['POST'])
def upsert_profile():
    """POST /api/user/profile — Create or update a user profile."""
    body = request.get_json(silent=True) or {}
    err  = validate_required_fields(body, ['user_id'])
    if err:
        return error(err, 400)

    try:
        svc.upsert(body)
        return success({'message': 'Profile saved.'})
    except Exception as exc:
        return error(str(exc), 500)


@user_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    """GET /api/user/profile/<user_id>"""
    try:
        profile = svc.get(user_id)
        if not profile:
            return error('User not found.', 404)
        return success({'profile': profile})
    except Exception as exc:
        return error(str(exc), 500)
