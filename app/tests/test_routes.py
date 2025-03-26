import pytest
from flask import url_for
from app.models import User, UserPreference, Source

def test_home_page_with_no_preferences(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirects to preferences
    assert 'preferences' in response.location

def test_home_page_with_preferences(client, test_preference, test_sources):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Your Article Feed' in response.data
    assert bytes(test_preference.area_of_interest, 'utf-8') in response.data

def test_preferences_page_get(client):
    response = client.get('/preferences')
    assert response.status_code == 200
    assert b'Set Your Preferences' in response.data

def test_preferences_page_post_valid(client):
    data = {
        'area_of_interest': 'Technology',
        'timeframe': 'daily',
        'sources': ['https://example.com/tech1', 'https://example.com/tech2']
    }
    response = client.post('/preferences', data=data)
    assert response.status_code == 302  # Redirects to home
    assert '/' == response.location

    # Verify database entries
    user = User.query.first()
    assert user is not None
    preference = UserPreference.query.first()
    assert preference is not None
    assert preference.area_of_interest == 'Technology'
    sources = Source.query.all()
    assert len(sources) == 2

def test_preferences_page_post_invalid(client):
    data = {
        'area_of_interest': '',  # Invalid: empty
        'timeframe': 'invalid',  # Invalid: wrong timeframe
        'sources': []  # Invalid: no sources
    }
    response = client.post('/preferences', data=data)
    assert response.status_code == 302
    assert 'preferences' in response.location

def test_update_timeframe(client, test_preference):
    data = {
        'timeframe': 'weekly',
        'preference_id': test_preference.id
    }
    response = client.post('/update_timeframe', data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True
    
    # Verify database update
    updated_preference = UserPreference.query.get(test_preference.id)
    assert updated_preference.timeframe == 'weekly'

def test_update_timeframe_invalid(client, test_preference):
    data = {
        'timeframe': 'invalid',
        'preference_id': test_preference.id
    }
    response = client.post('/update_timeframe', data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is False

def test_error_handling(client):
    # Test 404 error
    response = client.get('/nonexistent')
    assert response.status_code == 404
    
    # Test invalid method
    response = client.post('/')
    assert response.status_code == 405

def test_preferences_page_post_invalid_url(client):
    data = {
        'area_of_interest': 'Technology',
        'timeframe': 'daily',
        'sources': ['not-a-valid-url']
    }
    response = client.post('/preferences', data=data)
    assert response.status_code == 302
    assert 'preferences' in response.location

def test_empty_articles_display(client, test_preference):
    response = client.get('/')
    assert response.status_code == 200
    assert b'No articles found' in response.data

@pytest.mark.parametrize('timeframe', [
    'daily', 'weekly', 'fortnightly', 'monthly', 'quarterly'
])
def test_valid_timeframes(client, test_preference, timeframe):
    data = {
        'timeframe': timeframe,
        'preference_id': test_preference.id
    }
    response = client.post('/update_timeframe', data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True