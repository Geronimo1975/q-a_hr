from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

class SendGridBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently, **kwargs)
        self.api_key = settings.SENDGRID_API_KEY
        self.sg_client = SendGridAPIClient(self.api_key)

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of emails sent.
        """
        if not email_messages:
            return 0

        count = 0
        for message in email_messages:
            try:
                self._send(message)
                count += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e
        return count

    def _send(self, email_message):
        """
        Send an EmailMessage object using SendGrid.
        """
        if not email_message.recipients():
            return

        # Build the SendGrid message
        from_email = Email(email_message.from_email)
        subject = email_message.subject
        
        # Send to all recipients individually
        for recipient in email_message.recipients():
            to_email = To(recipient)
            
            # Check if the email is HTML
            if email_message.content_subtype == 'html':
                content = Content("text/html", email_message.body)
            else:
                content = Content("text/plain", email_message.body)
            
            sg_message = Mail(from_email, to_email, subject, content)
            
            # Add any reply-to addresses
            if email_message.reply_to:
                sg_message.reply_to = Email(email_message.reply_to[0])
            
            # Send the email
            self.sg_client.send(sg_message)