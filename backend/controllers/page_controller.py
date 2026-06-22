"""
controllers/page_controller.py — Serves HTML template pages.
"""

from flask import Blueprint, render_template

page_bp = Blueprint('pages', __name__)


@page_bp.route('/')
def index():
    return render_template('index.html')


@page_bp.route('/resume')
def resume():
    return render_template('resume.html')


@page_bp.route('/cover-letter')
def cover_letter():
    return render_template('coverletter.html')


@page_bp.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')
