from django.utils.translation import get_language, activate
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
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