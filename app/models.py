from datetime import datetime
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    preferences = db.relationship('UserPreference', backref='user', lazy=True)

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    area_of_interest = db.Column(db.String(128), nullable=False)
    timeframe = db.Column(db.String(32), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sources = db.relationship('Source', backref='user_preference', lazy=True)

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    preference_id = db.Column(db.Integer, db.ForeignKey('user_preference.id'), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)