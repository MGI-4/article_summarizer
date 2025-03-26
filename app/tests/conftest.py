import pytest
from app import create_app, db
from app.models import User, UserPreference, Source

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def test_user(app):
    user = User(username='test_user')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_preference(test_user):
    preference = UserPreference(
        user=test_user,
        area_of_interest='Technology',
        timeframe='daily'
    )
    db.session.add(preference)
    db.session.commit()
    return preference

@pytest.fixture
def test_sources(test_preference):
    sources = [
        Source(preference=test_preference, url='https://example.com/tech1'),
        Source(preference=test_preference, url='https://example.com/tech2')
    ]
    for source in sources:
        db.session.add(source)
    db.session.commit()
    return sources

@pytest.fixture
def auth_headers():
    return {'Authorization': 'Bearer test-token'}

@pytest.fixture
def sample_article_data():
    return {
        'title': 'Test Article',
        'content': 'Test content for summarization',
        'url': 'https://example.com/test',
        'date': '2025-02-21'
    }

@pytest.fixture
def mock_perplexity_response():
    return {
        'summary': '• First key point\n• Second key point\n• Third key point',
        'status': 'success'
    }