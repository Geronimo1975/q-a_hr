"""
Script to test sending password reset emails via allauth
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

# Now it's safe to import Django models
from django.contrib.sites.models import Site
from django.core.mail import send_mail

def test_password_reset():
    """
    Test sending a password reset email using Django's built-in functionality
    """
    if len(sys.argv) < 2:
        print("Usage: python test_password_reset.py <email_to_reset>")
        return
        
    email = sys.argv[1]
    
    # Check site configuration
    site = Site.objects.get(id=1)
    print(f"Current site configuration:")
    print(f"- Domain: {site.domain}")
    print(f"- Name: {site.name}")
    
    # Send test email directly using Django's send_mail
    from django.conf import settings
    
    print(f"\nEmail configuration:")
    print(f"- Backend: {settings.EMAIL_BACKEND}")
    print(f"- Default from: {settings.DEFAULT_FROM_EMAIL}")
    print(f"- SMTP Host: {settings.EMAIL_HOST}")
    print(f"- SMTP Port: {settings.EMAIL_PORT}")
    print(f"- TLS Enabled: {settings.EMAIL_USE_TLS}")
    print(f"- SendGrid API Key: {settings.SENDGRID_API_KEY[:5]}...{settings.SENDGRID_API_KEY[-5:]}")
    print(f"- SendGrid Sandbox Mode: {getattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG', 'Not set')}")
    
    try:
        # Import custom User model
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Check if the user exists
        try:
            user = User.objects.get(email=email)
            print(f"\nUser found: {user.email}")
        except User.DoesNotExist:
            print(f"\nNo user found with email: {email}")
            print("Creating a test email instead...")
            
        # Use the Django password reset form directly
        from django.contrib.auth.forms import PasswordResetForm
        
        # Create a mock request
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.META['HTTP_HOST'] = site.domain
        
        # Set the scheme for the request
        if settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL == 'https':
            request.is_secure = lambda: True
        
        print(f"\nSending password reset email to {email}...")
        form = PasswordResetForm({'email': email})
        if form.is_valid():
            # This will send the password reset email
            form.save(
                request=request,
                use_https=settings.ACCOUNT_DEFAULT_HTTP_PROTOCOL == 'https',
                from_email=settings.DEFAULT_FROM_EMAIL,
                domain_override=site.domain,
            )
            print("Password reset email sent successfully!")
        else:
            print(f"Form errors: {form.errors}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_password_reset()