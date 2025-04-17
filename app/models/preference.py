from app import db
from datetime import datetime
import json

class Preference(db.Model):
    """Preference model for storing user preferences for article summarization"""
    
    __tablename__ = 'preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    area_of_interest = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    sources = db.Column(db.Text, nullable=False)  # Stored as JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, user_id, area_of_interest, start_date, end_date, sources):
        """Initialize a new preference"""
        self.user_id = user_id
        self.area_of_interest = area_of_interest
        self.start_date = start_date
        self.end_date = end_date
        self.set_sources(sources)
    
    def set_sources(self, sources):
        """Convert sources list to JSON string for storage"""
        if isinstance(sources, list):
            self.sources = json.dumps(sources)
        else:
            # If it's a single string, convert to list then JSON
            self.sources = json.dumps([sources])
    
    def get_sources(self):
        """Get sources as a Python list"""
        return json.loads(self.sources)
    
    def to_dict(self):
        """Convert preference to dictionary for easier access in templates"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'area_of_interest': self.area_of_interest,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'sources': self.get_sources(),
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def __repr__(self):
        """Representation of the Preference model"""
        return f'<Preference {self.id}: {self.area_of_interest}>'