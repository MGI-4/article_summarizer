import os
import sys

# Add the parent directory to Python path for test imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test configurations
TEST_CONFIG = {
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'WTF_CSRF_ENABLED': False,
    'SECRET_KEY': 'test-key',
    'PERPLEXITY_API_KEY': 'test-api-key'
}

# Sample test data
SAMPLE_USER = {
    'username': 'test_user'
}

SAMPLE_PREFERENCE = {
    'area_of_interest': 'Technology',
    'timeframe': 'daily'
}

SAMPLE_SOURCES = [
    'https://example.com/tech1',
    'https://example.com/tech2'
]

SAMPLE_ARTICLE = {
    'title': 'Test Article',
    'content': 'Test content for summarization',
    'url': 'https://example.com/test',
    'summary': '• First point\n• Second point',
    'date': '2025-02-21'
}