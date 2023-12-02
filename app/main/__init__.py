from flask import Blueprint

bp = Blueprint('main', __name__)
central_bp = Blueprint('central', __name__)

from app.main import routes
