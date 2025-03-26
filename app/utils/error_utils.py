from functools import wraps
from flask import jsonify, current_app
import logging
import traceback
from typing import Any, Callable

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = 400, payload: Any = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> dict:
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        return rv

def handle_errors(f: Callable) -> Callable:
    """
    Decorator for handling errors in route functions
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            logger.error(f"API Error: {e.message}")
            response = jsonify(e.to_dict())
            response.status_code = e.status_code
            return response
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            if current_app.debug:
                raise
            return jsonify({
                'message': 'An unexpected error occurred',
                'status_code': 500
            }), 500
    return decorated_function

def validate_request_data(data: dict, required_fields: list) -> None:
    """
    Validate request data for required fields
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise APIError(
            message=f"Missing required fields: {', '.join(missing_fields)}",
            status_code=400
        )

class DatabaseError(APIError):
    """Database operation error"""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message=message, status_code=500)
        logger.error(f"Database Error: {message}")
        if original_error:
            logger.error(f"Original error: {str(original_error)}")
            logger.error(traceback.format_exc())

class ValidationError(APIError):
    """Data validation error"""
    def __init__(self, message: str):
        super().__init__(message=message, status_code=400)

class AuthenticationError(APIError):
    """Authentication error"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, status_code=401)

class AuthorizationError(APIError):
    """Authorization error"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)

def setup_error_logging(app):
    """
    Configure error logging for the application
    """
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        # Ensure logs directory exists
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        # Configure file handler
        file_handler = RotatingFileHandler(
            'logs/article_summarizer.log',
            maxBytes=1024 * 1024,  # 1MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Article Summarizer startup')