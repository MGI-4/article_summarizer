from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config.config import Config
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

# Add context processor for template variables
@app.context_processor
def inject_now():
    return {'current_year': datetime.utcnow().year}

# Import blueprints
from app.controllers.auth import auth_bp
from app.controllers.main import main_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

# Import models for Flask-Login
from app.models.user import User
from app.models.preference import Preference

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))