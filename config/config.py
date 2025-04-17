import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application."""
    
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}/{}'.format(
        os.environ.get('DB_USERNAME', 'root'),
        os.environ.get('DB_PASSWORD', ''),
        os.environ.get('DB_HOST', 'localhost'),
        os.environ.get('DB_NAME', 'article_summarizer')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Perplexity API configuration
    PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY', '')
    
    # News API configuration
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
    
    # Google Custom Search API configuration
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
    GOOGLE_SEARCH_ENGINE_ID = os.environ.get('GOOGLE_SEARCH_ENGINE_ID', '')