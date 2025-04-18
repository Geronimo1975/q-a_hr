from django.utils.translation import get_language
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import threading

# Thread-local storage to keep track of which text has already been translated
local = threading.local()

class GoogleTranslationMiddleware(MiddlewareMixin):
    """
    Middleware that integrates Google Translation with Django's translation system.
    This allows for automatic fallback to Google Translate when Django translations are missing.
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        # Initialize thread-local storage for tracking translations
        if not hasattr(local, 'translated_texts'):
            local.translated_texts = set()
    
    def process_request(self, request):
        """Reset translation tracking at the start of each request"""
        local.translated_texts = set()
        return None
    
    def process_response(self, request, response):
        """Clean up after each request"""
        if hasattr(local, 'translated_texts'):
            local.translated_texts = set()
        return response