import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from app.utils.article_utils import (
    ArticleFetcher,
    RelatedArticleFinder,
    validate_url,
    get_timeframe_dates,
    format_summary,
    cache_article,
    get_cached_article
)
from app.utils.error_utils import (
    APIError,
    handle_errors,
    validate_request_data,
    DatabaseError,
    ValidationError
)

# ArticleFetcher Tests
class TestArticleFetcher:
    @pytest.fixture
    def article_fetcher(self):
        return ArticleFetcher('test-api-key')

    @patch('requests.get')
    def test_fetch_article_content_success(self, mock_get, article_fetcher):
        # Mock successful response
        mock_response = Mock()
        mock_response.text = '''
            <html>
                <head><title>Test Article</title></head>
                <body>
                    <article>Test content</article>
                </body>
            </html>
        '''
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = article_fetcher.fetch_article_content('https://example.com/article')
        
        assert result['title'] == 'Test Article'
        assert 'Test content' in result['content']
        assert result['url'] == 'https://example.com/article'

    @patch('requests.get')
    def test_fetch_article_content_failure(self, mock_get, article_fetcher):
        mock_get.side_effect = Exception('Network error')
        
        result = article_fetcher.fetch_article_content('https://example.com/article')
        assert result is None

    @patch('requests.post')
    def test_generate_summary_success(self, mock_post, article_fetcher):
        mock_response = Mock()
        mock_response.json.return_value = {
            'summary': 'Test summary',
            'status': 'success'
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        summary = article_fetcher.generate_summary('Test content')
        assert summary == 'Test summary'

    @patch('requests.post')
    def test_generate_summary_failure(self, mock_post, article_fetcher):
        mock_post.side_effect = Exception('API error')
        
        summary = article_fetcher.generate_summary('Test content')
        assert summary == 'Summary unavailable'

    def test_process_articles(self, article_fetcher):
        with patch.object(article_fetcher, 'fetch_article_content') as mock_fetch:
            with patch.object(article_fetcher, 'generate_summary') as mock_summary:
                mock_fetch.return_value = {
                    'title': 'Test',
                    'content': 'Content',
                    'url': 'https://example.com',
                    'date': '2025-02-21'
                }
                mock_summary.return_value = 'Summary'

                articles = article_fetcher.process_articles(
                    ['https://example.com'],
                    'Technology'
                )
                
                assert len(articles) == 1
                assert articles[0]['title'] == 'Test'
                assert articles[0]['summary'] == 'Summary'

# RelatedArticleFinder Tests
def test_related_article_finder():
    finder = RelatedArticleFinder()
    articles = finder.find_related_articles('Technology', 7)
    
    assert isinstance(articles, list)
    assert len(articles) > 0
    assert all('title' in article for article in articles)
    assert all('url' in article for article in articles)

# URL Validation Tests
@pytest.mark.parametrize('url,expected', [
    ('https://example.com', True),
    ('http://example.com', True),
    ('not-a-url', False),
    ('', False),
    ('ftp://example.com', False)
])
def test_validate_url(url, expected):
    with patch('requests.head') as mock_head:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_head.return_value = mock_response
        
        if expected:
            mock_head.return_value.status_code = 200
        else:
            mock_head.side_effect = Exception('Invalid URL')
        
        assert validate_url(url) == expected

# Timeframe Tests
@pytest.mark.parametrize('timeframe,expected_days', [
    ('daily', 1),
    ('weekly', 7),
    ('fortnightly', 14),
    ('monthly', 30),
    ('quarterly', 90)
])
def test_get_timeframe_dates(timeframe, expected_days):
    start_date, end_date = get_timeframe_dates(timeframe)
    
    assert isinstance(start_date, datetime)
    assert isinstance(end_date, datetime)
    assert end_date - start_date == timedelta(days=expected_days)

# Summary Formatting Tests
@pytest.mark.parametrize('input_summary,expected_contains', [
    ('Point 1. Point 2', '<li>Point 1</li>'),
    ('• First point\n• Second point', '<li>First point</li>'),
    ('', '<p>Summary not available</p>'),
    ('- Point 1\n- Point 2', '<li>Point 1</li>')
])
def test_format_summary(input_summary, expected_contains):
    formatted = format_summary(input_summary)
    assert expected_contains in formatted

# Cache Tests
def test_cache_article(tmp_path):
    article = {
        'url': 'https://example.com',
        'title': 'Test',
        'content': 'Content'
    }
    
    cache_dir = tmp_path / 'cache'
    cache_article(article, str(cache_dir))
    
    cached = get_cached_article('https://example.com', str(cache_dir))
    assert cached['title'] == 'Test'
    assert cached['content'] == 'Content'

# Error Handling Tests
def test_api_error():
    error = APIError('Test error', 400)
    assert error.to_dict()['message'] == 'Test error'
    assert error.to_dict()['status_code'] == 400

def test_validate_request_data():
    valid_data = {'field1': 'value1', 'field2': 'value2'}
    required_fields = ['field1', 'field2']
    
    # Should not raise an exception
    validate_request_data(valid_data, required_fields)
    
    invalid_data = {'field1': 'value1'}
    with pytest.raises(APIError):
        validate_request_data(invalid_data, required_fields)

def test_error_decorator():
    @handle_errors
    def test_function():
        raise APIError('Test error', 400)
    
    response = test_function()
    assert response.status_code == 400
    assert 'Test error' in response.get_json()['message']

# Database Error Tests
def test_database_error():
    error = DatabaseError('Database connection failed')
    assert error.status_code == 500
    assert 'Database connection failed' in error.message

# Validation Error Tests
def test_validation_error():
    error = ValidationError('Invalid input')
    assert error.status_code == 400
    assert 'Invalid input' in error.message