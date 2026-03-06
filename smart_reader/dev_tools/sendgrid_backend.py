"""
SendGrid Email Backend for Django
Allows sending emails to ANY email address (Gmail, Yahoo, Outlook, etc.)
"""

from django.core.mail.backends.base import BaseEmailBackend
from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.core.exceptions import ImproperlyConfigured


class SendgridBackend(BaseEmailBackend):
    """
    A Django email backend that uses SendGrid's Web API.
    Allows sending OTPs to any email address.
    """
    
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently=fail_silently)
        
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        if not self.api_key or self.api_key == 'SENDGRID_API_KEY_HERE':
            raise ImproperlyConfigured(
                'SENDGRID_API_KEY not configured. '
                'Get it from: https://app.sendgrid.com/settings/api_keys'
            )
        
        self.client = sendgrid.SendGridAPIClient(self.api_key)
    
    def send_messages(self, email_messages):
        """
        Send messages via SendGrid Web API
        """
        if not email_messages:
            return 0
        
        sent_messages = 0
        
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    sent_messages += 1
            except Exception as e:
                if not self.fail_silently:
                    raise
                else:
                    print(f"SendGrid Error: {e}")
        
        return sent_messages
    
    def _send(self, message):
        """
        Send a single message via SendGrid
        """
        if not message.recipients():
            return False
        
        try:
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            # Create email message
            from_email_str = message.from_email
            if '<' in from_email_str:
                # Extract email from "Name <email@domain.com>" format
                from_email_str = from_email_str.split('<')[1].split('>')[0]
            
            from_email = Email(from_email_str)
            
            # Send to each recipient
            for recipient in message.recipients():
                to_email = To(recipient)
                
                # Plain text content
                content = Content("text/plain", message.body)
                
                mail = Mail(
                    from_email=from_email,
                    to_emails=to_email,
                    subject=message.subject,
                    plain_text_content=content
                )
                
                # Add HTML content if available
                if hasattr(message, 'alternatives'):
                    for alt_content, alt_type in message.alternatives:
                        if alt_type == 'text/html':
                            mail.html_content = alt_content
                
                # Add custom headers if any
                if hasattr(message, 'extra_headers') and message.extra_headers:
                    for header, value in message.extra_headers.items():
                        mail.header.add_header(header, value)
                
                # Send via SendGrid
                response = self.client.send(mail)
                
                # Check if successful (202 = Accepted)
                if response.status_code not in [200, 201, 202]:
                    error_msg = f"SendGrid Error: {response.status_code}"
                    if hasattr(response, 'body'):
                        error_msg += f" - {response.body}"
                    print(error_msg)
                    return False
            
            return True
            
        except Exception as e:
            print(f"SendGrid Exception: {e}")
            if not self.fail_silently:
                raise
            return False
