#!/usr/bin/env python
"""
Test Email Configuration for SmartReader OTP System

This script tests if your email configuration is working properly.
Run this to verify that OTP emails can be sent successfully.

Usage:
    python test_email.py

or with Django shell:
    python manage.py shell < test_email.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    print("\n" + "="*60)
    print("📧 TESTING EMAIL CONFIGURATION")
    print("="*60 + "\n")
    
    # Display current email settings
    print("Current Email Settings:")
    print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"  USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
    
    if hasattr(settings, 'EMAIL_HOST'):
        print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"  EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"  EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    
    print("\n" + "-"*60 + "\n")
    
    # Test email address
    test_email = input("Enter email address to send test OTP (or press Enter to skip): ").strip()
    
    if not test_email:
        print("❌ Test skipped. No email provided.")
        return
    
    print(f"\n🔄 Sending test OTP to: {test_email}")
    
    # Generate test OTP
    import random
    test_otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    
    subject = "SmartReader - Test OTP Email"
    message = f"""
Hello!

This is a TEST OTP email from SmartReader.

Your test OTP is: {test_otp}

If you received this email, your OTP email configuration is working correctly! ✅

Best regards,
SmartReader Team
"""
    
    html_message = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #f9fafb; padding: 30px; border-radius: 10px;">
            <h2 style="color: #6366f1; text-align: center;">📚 SmartReader - Test Email</h2>
            <p>Hello!</p>
            <p>This is a <strong>TEST OTP</strong> email from SmartReader.</p>
            <div style="background: #6366f1; color: white; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 8px; letter-spacing: 8px; margin: 20px 0;">
                {test_otp}
            </div>
            <p style="color: #10b981; font-weight: bold;">✅ If you received this email, your OTP configuration is working correctly!</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px; text-align: center;">SmartReader Team</p>
        </div>
    </body>
    </html>
    """
    
    try:
        from django.core.mail import EmailMultiAlternatives
        
        email_msg = EmailMultiAlternatives(
            subject, 
            message, 
            settings.DEFAULT_FROM_EMAIL,
            [test_email]
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send(fail_silently=False)
        
        print(f"\n✅ SUCCESS! Test email sent to {test_email}")
        print(f"📧 Test OTP: {test_otp}")
        print("\nPlease check your email inbox (and spam folder).")
        print("\nIf you don't receive the email:")
        print("  1. Check your .env file EMAIL_HOST_PASSWORD")
        print("  2. Make sure USE_REAL_EMAIL=True in .env")
        print("  3. Verify Gmail App Password is correct (16 characters, no spaces)")
        print("  4. Check if 'Less secure app access' is enabled for Gmail")
        print("  5. Try checking spam/junk folder")
        
    except Exception as e:
        print(f"\n❌ ERROR sending test email!")
        print(f"Error: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Check .env file exists in smart_reader folder")
        print("  2. Verify EMAIL_HOST_PASSWORD is set correctly")
        print("  3. Make sure USE_REAL_EMAIL=True")
        print("  4. Get Gmail App Password from: https://myaccount.google.com/apppasswords")
        print("  5. Restart Django server after changing .env file")
        
        import traceback
        print("\nFull error details:")
        traceback.print_exc()
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    test_email_config()
