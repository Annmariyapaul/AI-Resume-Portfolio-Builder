"""
services/portfolio_service.py — Portfolio page generation via Gemini.
"""

from datetime import datetime
from gemini_api       import generate_text
from firebase_config  import save_document, get_user_documents, delete_document
from utils.logger     import get_logger

logger = get_logger(__name__)


class PortfolioService:

    def generate(self, data: dict) -> dict:
        """Generate a polished bio/about-me paragraph using Gemini, store data."""
        bio_prompt = (
            f"Write a compelling 3-sentence professional bio for {data.get('name', '')} "
            f"who works as {data.get('title', '')}. "
            f"Raw info: {data.get('bio', '')}. "
            "Be punchy, first-person, modern."
        )
        enhanced_bio = generate_text(bio_prompt, temperature=0.7)

        portfolio_data = {
            **data,
            'enhanced_bio': enhanced_bio,
            'created_at':   datetime.utcnow().isoformat(),
        }

        doc_id = save_document('portfolios', portfolio_data)
        return {'doc_id': doc_id, 'portfolio_data': portfolio_data}

    def save(self, user_id: str, portfolio_data: dict) -> str:
        portfolio_data['user_id']    = user_id
        portfolio_data['updated_at'] = datetime.utcnow().isoformat()
        return save_document('portfolios', portfolio_data)

    def get_all(self, user_id: str) -> list:
        return get_user_documents('portfolios', user_id)

    def delete(self, doc_id: str):
        delete_document('portfolios', doc_id)
