from django.utils.translation import get_language, activate
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponse
from django.db import connection
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

class TranslationDebugMiddleware(MiddlewareMixin):
    """
    Middleware that logs information about language changes and translation activity.
    """
    
    def process_request(self, request):
        """Process the request and log language information"""
        language_code = get_language()
        logger.info(f"Current language code: {language_code}")
        
        # Log if translations are being attempted
        if hasattr(request, 'LANGUAGE_CODE'):
            logger.info(f"Request language code: {request.LANGUAGE_CODE}")
        
        # Also log the URL to identify the language prefix
        logger.info(f"Current URL path: {request.path}")
        
        return None

class SessionErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            # Check if it's a database connection error
            if 'SSL connection has been closed unexpectedly' in str(e) or 'connection already closed' in str(e):
                logger.error(f"Database connection error: {str(e)}")
                try:
                    # Try to close any open connections and reconnect
                    connection.close()
                    connection.connect()
                    # Retry the request
                    return self.get_response(request)
                except Exception as retry_error:
                    logger.error(f"Failed to reconnect to database: {str(retry_error)}")
                    return HttpResponse("Database connection error. Please try again later.", status=500)
            # If it's a session error, return a response without using the session
            elif 'session' in str(e).lower():
                logger.error(f"Session error: {str(e)}")
                return HttpResponse("Session error. Please clear your cookies and try again.", status=500)
            # Otherwise, let the exception propagate
            raise e