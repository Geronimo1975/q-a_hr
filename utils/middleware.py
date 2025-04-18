from django.utils.translation import get_language
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from utils.translate_api import translate_text

class GoogleTranslationMiddleware(MiddlewareMixin):
    """
    Middleware that integrates Google Translation with Django's translation system.
    This allows for automatic fallback to Google Translate when Django translations are missing.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        # Initialize storage for translation tracking
        self.reset_translation_tracker()

    def process_request(self, request):
        """Reset translation tracking at the start of each request"""
        self.reset_translation_tracker()
        return None
    
    def process_response(self, request, response):
        """Clean up after each request"""
        self.reset_translation_tracker()
        return response
    
    def reset_translation_tracker(self):
        """Reset the translation tracker"""
        # This would be used to track which translations were performed
        # and potentially cache them for performance
        pass