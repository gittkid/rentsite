"""
Blueprint для основных страниц
"""

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes 