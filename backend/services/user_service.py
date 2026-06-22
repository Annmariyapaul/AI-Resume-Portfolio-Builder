"""
services/user_service.py — User profile persistence.
"""

from datetime import datetime
from firebase_config import save_document, get_document


class UserService:

    def upsert(self, data: dict):
        data['updated_at'] = datetime.utcnow().isoformat()
        save_document('users', data, doc_id=data['user_id'])

    def get(self, user_id: str) -> dict | None:
        return get_document('users', user_id)
