"""
Script to test sending emails through SendGrid
"""
import os
import sys
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'driver_recruitment.settings')
django.setup()

def test_send_email():
    """
    Test sending an email using SendGrid
    """
    subject = 'Test Email from FastDelivery'
    message = 'This is a test email from the FastDelivery application.'
    html_message = '''
    <html>
    <body>
        <h2 style="color: #0064FF;">FastDelivery</h2>
        <p>This is a test email from the FastDelivery application.</p>
        <p>If you received this, email sending is working correctly!</p>
        <p>Email configuration:</p>
        <ul>
            <li>Backend: {}</li>
            <li>Default from: {}</li>
            <li>Host: {}</li>
            <li>Port: {}</li>
            <li>TLS: {}</li>
            <li>API Key: {}...</li>
        </ul>
    </body>
    </html>
    '''.format(
        settings.EMAIL_BACKEND,
        settings.DEFAULT_FROM_EMAIL,
        settings.EMAIL_HOST,
        settings.EMAIL_PORT,
        settings.EMAIL_USE_TLS,
        settings.SENDGRID_API_KEY[:10] if settings.SENDGRID_API_KEY else 'Not set'
    )
    
    from_email = settings.DEFAULT_FROM_EMAIL
    
    if len(sys.argv) < 2:
        print("Usage: python test_email.py <recipient_email>")
        return
    
    recipient_list = [sys.argv[1]]
    
    try:
        print(f"Sending test email to {recipient_list[0]}...")
        
        # Verificare dacă suntem în modul sandbox
        if hasattr(settings, 'SENDGRID_SANDBOX_MODE_IN_DEBUG') and settings.SENDGRID_SANDBOX_MODE_IN_DEBUG:
            print("WARNING: SENDGRID_SANDBOX_MODE_IN_DEBUG is enabled. Emails will be logged but not sent!")
        
        result = send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        
        if result:
            print("Email sent successfully!")
        else:
            print("Email sending failed!")
            
    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == "__main__":
    test_send_email()