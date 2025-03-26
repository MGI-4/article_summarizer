import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql://username:password@localhost/article_summarizer'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API configuration
    PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
    PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'  # Update with actual API endpoint
    
    # Application configuration
    MAX_SOURCES_PER_USER = 10
    SUMMARY_MAX_LENGTH = 500
    ALLOWED_TIMEFRAMES = ['daily', 'weekly', 'fortnightly', 'monthly', 'quarterly']
    
    # Cache configuration (if you implement caching)
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # Production-specific settings
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}