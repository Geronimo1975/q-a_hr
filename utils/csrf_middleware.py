"""
Custom CSRF middleware to help resolve CSRF issues in Replit environment
"""
import logging
from django.middleware.csrf import CsrfViewMiddleware
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class CustomCsrfMiddleware(MiddlewareMixin):
    """
    Custom middleware to handle CSRF token validation issues in iframe environments.
    This is useful when running in Replit or other environments where CSRF validation 
    might cause problems due to cross-origin issues.
    """
    
    def process_request(self, request):
        """
        Process the request and debug CSRF token issues
        """
        # Log the relevant headers for debugging
        if settings.DEBUG and 'admin' in request.path:
            logger.debug(f"Request method: {request.method}")
            logger.debug(f"CSRF_COOKIE: {request.COOKIES.get('csrftoken')}")
            
            # Get all headers
            headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
            logger.debug(f"Request headers: {headers}")
            
            # Set custom attribute to indicate CSRF debugging mode
            request.csrf_debug = True
            
            # Log the referer if it exists
            if 'HTTP_REFERER' in request.META:
                logger.debug(f"Referer: {request.META['HTTP_REFERER']}")