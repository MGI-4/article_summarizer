from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model, UserMixin):
    """User model for storing user account information"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationship with Preferences
    preferences = db.relationship('Preference', backref='user', lazy='dynamic', cascade="all, delete-orphan")
    
    def __init__(self, username, email, password):
        """Initialize a new user"""
        self.username = username
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """Set the password hash for the user"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the password is correct"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Update the last login time to current time"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        """Representation of the User model"""
        return f'<User {self.username}>'