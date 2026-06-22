"""
routes.py — Central Blueprint Registration
All route logic lives in controllers/; this file wires everything together.
"""

from controllers.page_controller    import page_bp
from controllers.resume_controller  import resume_bp
from controllers.cover_controller   import cover_bp
from controllers.portfolio_controller import portfolio_bp
from controllers.user_controller    import user_bp


def register_routes(app):
    app.register_blueprint(page_bp)
    app.register_blueprint(resume_bp,    url_prefix='/api/resume')
    app.register_blueprint(cover_bp,     url_prefix='/api/cover-letter')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(user_bp,      url_prefix='/api/user')
