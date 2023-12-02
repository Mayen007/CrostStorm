from flask import Blueprint
# from .handlers import init_errors_bp

bp = Blueprint('errors', __name__)
new_bp = Blueprint('error', __name__)


from app.errors import handlers  # Importing at the end to avoid circular imports


def error_bp():
    return None