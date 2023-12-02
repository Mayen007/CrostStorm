from flask import Blueprint

auth_bp = Blueprint('auth_bp', __name__)
user_bp = Blueprint('user_bp', __name__)
new_bp = Blueprint('new_bp', __name__)

from app.auth import routes

from app.auth.routes import user_route  # Import the function from routes.py
