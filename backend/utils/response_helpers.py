"""utils/response_helpers.py — Consistent JSON response format."""

from flask import jsonify


def success(data: dict, status: int = 200):
    return jsonify({'status': 'success', **data}), status


def error(message: str, status: int = 400):
    return jsonify({'status': 'error', 'message': message}), status
