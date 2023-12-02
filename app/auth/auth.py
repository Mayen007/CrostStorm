from flask_login import LoginManager
from app.models import User
login = LoginManager()
login.login_view = 'new_bp.login'
