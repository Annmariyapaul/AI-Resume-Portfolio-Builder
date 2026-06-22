"""
firebase_config.py — Firebase Admin SDK initialisation & Firestore helpers.
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
from utils.logger import get_logger

logger = get_logger(__name__)

_db = None   # module-level singleton


def _init_firebase():
    """Initialise Firebase Admin SDK (idempotent)."""
    global _db
    if _db is not None:
        return _db

    if firebase_admin._apps:          # already initialised
        _db = firestore.client()
        return _db

    cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', '')
    cred_json  = os.getenv('FIREBASE_CREDENTIALS_JSON', '')

    logger.info(f"Attempting Firebase init. cred_path={cred_path}, cred_json={bool(cred_json)}")

    if cred_path:
        # Resolve path relative to this file's directory (backend/)
        if not os.path.isabs(cred_path):
            # If relative path, resolve from backend directory
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            abs_path = os.path.abspath(os.path.join(backend_dir, cred_path))
        else:
            abs_path = os.path.abspath(cred_path)
        
        logger.info(f"Resolved credential path: {abs_path}")
        logger.info(f"Credentials file exists: {os.path.exists(abs_path)}")
        
        if os.path.exists(abs_path):
            try:
                cred = credentials.Certificate(abs_path)
            except Exception as e:
                logger.error(f"Failed to load credentials from {abs_path}: {e}")
                raise
        else:
            logger.error(f"Credentials file not found at {abs_path}")
            return None
    elif cred_json:
        try:
            cred = credentials.Certificate(json.loads(cred_json))
        except Exception as e:
            logger.error(f"Failed to parse Firebase credentials JSON: {e}")
            raise
    else:
        logger.error(
            "No Firebase credentials found. "
            "Set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON in .env"
        )
        return None

    try:
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        logger.info("Firebase initialised successfully.")
    except Exception as e:
        logger.error(f"Firebase initialization failed: {e}")
        raise
    
    return _db


def get_db():
    """Return the Firestore client, initialising if necessary."""
    return _init_firebase()


# ── Generic CRUD helpers ─────────────────────────────────────────────────────

def save_document(collection: str, data: dict, doc_id: str | None = None) -> str:
    """
    Create or overwrite a Firestore document.

    Args:
        collection: Collection name (e.g. 'resumes').
        data:       Dictionary to store.
        doc_id:     Optional document ID; auto-generated when omitted.

    Returns:
        The document ID.
    """
    db = get_db()
    col_ref = db.collection(collection)
    if doc_id:
        col_ref.document(doc_id).set(data)
        return doc_id
    _, doc_ref = col_ref.add(data)
    return doc_ref.id


def get_document(collection: str, doc_id: str) -> dict | None:
    """Fetch a single document; returns None if it doesn't exist."""
    db = get_db()
    doc = db.collection(collection).document(doc_id).get()
    return doc.to_dict() if doc.exists else None


def get_user_documents(collection: str, user_id: str) -> list[dict]:
    """Return all documents in *collection* belonging to *user_id*."""
    db = get_db()
    docs = (
        db.collection(collection)
        .where('user_id', '==', user_id)
        .order_by('created_at', direction=firestore.Query.DESCENDING)
        .stream()
    )
    return [{'id': d.id, **d.to_dict()} for d in docs]


def delete_document(collection: str, doc_id: str) -> bool:
    """Delete a document. Returns True on success."""
    try:
        get_db().collection(collection).document(doc_id).delete()
        return True
    except Exception as exc:
        logger.error("Delete failed: %s", exc)
        return False


def update_document(collection: str, doc_id: str, data: dict) -> bool:
    """Partially update an existing document."""
    try:
        get_db().collection(collection).document(doc_id).update(data)
        return True
    except Exception as exc:
        logger.error("Update failed: %s", exc)
        return False
