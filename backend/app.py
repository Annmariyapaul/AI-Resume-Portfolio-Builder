"""
AI Resume & Portfolio Builder — Flask Application Entry Point
"""

import os
from dotenv import load_dotenv

# Load variables from .env (in the project root) into the environment.
# This MUST run before importing routes — routes pulls in controllers ->
# services -> gemini_api.py / firebase_config.py, and those read
# os.getenv(...) the instant they're imported. If load_dotenv() ran after
# that import, GEMINI_API_KEY / FIREBASE_CREDENTIALS_PATH would already
# have been read as empty strings.
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
print(f"Loading environment from: {os.path.abspath(env_path)}")
load_dotenv(env_path)

print(f"GEMINI_API_KEY set: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"FIREBASE_CREDENTIALS_PATH: {os.getenv('FIREBASE_CREDENTIALS_PATH')}")
print(f"PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION will be set to: python")

# Force protobuf's pure-Python implementation. The compiled C extension
# (upb) that protobuf ships doesn't yet support Python 3.14's stricter
# C-API rules and crashes on import with:
#   TypeError: Metaclasses with custom tp_new are not supported.
# This must also be set before the google.generativeai / firebase-admin
# imports below pull protobuf in. Safe to remove once you're on a protobuf
# release that ships a 3.14-compatible C extension.
os.environ.setdefault('PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION', 'python')

from flask import Flask
from flask_cors import CORS
from routes import register_routes


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'),
    )

    # ── Config ──────────────────────────────────────────────────────────────
    app.config['SECRET_KEY']         = os.getenv('SECRET_KEY', 'dev-secret-change-me')
    app.config['GENERATED_FILES_DIR']= os.path.join(os.path.dirname(__file__), '..', 'generated_files')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024   # 16 MB upload limit

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Ensure output folder exists ──────────────────────────────────────────
    os.makedirs(app.config['GENERATED_FILES_DIR'], exist_ok=True)

    # ── Register all blueprints ──────────────────────────────────────────────
    register_routes(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)