"""
gemini_api.py — Thin wrapper around Google Gemini generative model.
All prompts are built in services/; this module only handles HTTP transport.
"""

import os
import google.generativeai as genai
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Initialise once at import time ──────────────────────────────────────────
_API_KEY = os.getenv('GEMINI_API_KEY', '')
if _API_KEY:
    genai.configure(api_key=_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set — AI features will fail at runtime.")

_DEFAULT_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')


def generate_text(prompt: str, model_name: str = _DEFAULT_MODEL,
                  temperature: float = 0.7, max_tokens: int = 8192) -> str:
    """
    Send a text prompt to Gemini and return the response as a plain string.

    Args:
        prompt:       Full prompt string.
        model_name:   Gemini model identifier.
        temperature:  Creativity (0 = deterministic, 1 = creative).
        max_tokens:   Maximum tokens in the response.

    Returns:
        Generated text string.

    Raises:
        RuntimeError: When the Gemini call fails.
    """
    try:
        model = genai.GenerativeModel(
            model_name,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        raise RuntimeError(f"Gemini API call failed: {exc}") from exc


def generate_json(prompt: str, model_name: str = _DEFAULT_MODEL,
                  temperature: float = 0.1, max_tokens: int = 8192) -> str:
    """
    Generate structured JSON using Gemini.
    """

    try:
        model = genai.GenerativeModel(
            model_name,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json"
            )
        )

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as exc:
        logger.error("Gemini JSON API error: %s", exc)
        raise RuntimeError(f"Gemini JSON generation failed: {exc}") from exc