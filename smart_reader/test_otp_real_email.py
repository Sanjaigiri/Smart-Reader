#!/usr/bin/env python
"""
Test script to verify OTP email sending works correctly
This will send a test OTP to sriakilkaviraj2005@gmail.com
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import time

print("\n" + "="*70)
print("📧 TESTING OTP EMAIL SENDING FOR SMARTREADER")
print("="*70)

# Check email configuration
print("\n📋 Current Email Configuration:")
print(f"  USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
print(f"  EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
print(f"  EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
print(f"  EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")

password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
if password:
    print(f"  EMAIL_HOST_PASSWORD: {'*' * len(password)} ({len(password)} chars)")
else:
    print(f"  EMAIL_HOST_PASSWORD: ❌ NOT SET!")

print(f"  DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")

# Check if real email is enabled
if not getattr(settings, 'USE_REAL_EMAIL', False):
    print("\n⚠️  WARNING: USE_REAL_EMAIL is set to False!")
    print("   OTPs will only be printed to console, not sent to email.")
    print("\n🔧 To enable real email sending:")
    print("   1. Open .env file in smart_reader folder")
    print("   2. Change: USE_REAL_EMAIL=True")
    print("   3. Add your Gmail App Password")
    print("   4. Save and restart Django server")
    print("   5. Run this script again")
    sys.exit(1)

if not password:
    print("\n❌ ERROR: EMAIL_HOST_PASSWORD is not set!")
    print("   Please follow the steps in SETUP_EMAIL_FOR_OTP.md")
    sys.exit(1)

# Generate test OTP
test_otp = '123456'
test_email = 'sriakilkaviraj2005@gmail.com'

print(f"\n🎯 Target Email: {test_email}")
print(f"🔢 Test OTP: {test_otp}")

subject = 'SmartReader - Test OTP Email'
message = f'''Hello!

This is a TEST OTP from SmartReader to verify email configuration.

Your test OTP is: {test_otp}

✅ If you received this email, the OTP system is working correctly!
You can now use the signup feature and receive OTPs instantly.

Best regards,
SmartReader Team
'''

html_message = f'''
<html>
<body style="font-family: Arial, sans-serif; padding: 20px; background: #f3f4f6;">
    <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h2 style="color: #6366f1; text-align: center; margin-bottom: 20px;">📚 SmartReader</h2>
        <h3 style="color: #333; text-align: center;">Test OTP Email</h3>
        <p style="color: #666;">Hello!</p>
        <p style="color: #666;">This is a <strong>TEST OTP</strong> to verify your email configuration is working.</p>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 36px; font-weight: bold; text-align: center; padding: 25px; border-radius: 8px; letter-spacing: 10px; margin: 25px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            {test_otp}
        </div>
        <div style="background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; border-radius: 4px; margin: 20px 0;">
            <p style="color: #065f46; margin: 0; font-weight: bold;">✅ Email Configuration Working!</p>
            <p style="color: #065f46; margin: 5px 0 0 0; font-size: 14px;">Your OTP system is now ready for production use.</p>
        </div>
        <p style="color: #999; font-size: 13px; margin-top: 30px;">This is a test email sent at {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 25px 0;">
        <p style="color: #9ca3af; font-size: 12px; text-align: center; margin: 0;">SmartReader Team | Final Year Project</p>
    </div>
</body>
</html>
'''

print(f"\n🔄 Sending test email...")
print(f"   Please wait (this may take 5-10 seconds)...\n")

start_time = time.time()

try:
    email_msg = EmailMultiAlternatives(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [test_email]
    )
    email_msg.attach_alternative(html_message, "text/html")
    email_msg.send(fail_silently=False)
    
    elapsed = time.time() - start_time
    
    print(f"✅ SUCCESS! Email sent in {elapsed:.2f} seconds!")
    print(f"\n📧 Email Details:")
    print(f"   To: {test_email}")
    print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
    print(f"   Subject: {subject}")
    print(f"   Test OTP: {test_otp}")
    
    print(f"\n📬 Next Steps:")
    print(f"   1. Check inbox of: {test_email}")
    print(f"   2. Also check SPAM/JUNK folder (Gmail may filter it)")
    print(f"   3. Look for email with subject: '{subject}'")
    print(f"   4. If received, OTP system is working perfectly!")
    
    print(f"\n🎉 Your SmartReader project is ready for signup with real OTP emails!")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ ERROR! Email failed after {elapsed:.2f} seconds")
    print(f"   Error: {str(e)}")
    
    print(f"\n🔧 Troubleshooting Steps:")
    print(f"   1. Check EMAIL_HOST_PASSWORD in .env file")
    print(f"   2. Make sure it's a Gmail App Password (16 chars, no spaces)")
    print(f"   3. Verify 2FA is enabled on your Gmail account")
    print(f"   4. Try generating a new App Password")
    print(f"   5. Check internet connection")
    
    print(f"\n📚 For detailed setup instructions:")
    print(f"   Read: SETUP_EMAIL_FOR_OTP.md")
    
    import traceback
    print(f"\n📋 Full Error Details:")
    traceback.print_exc()

print("\n" + "="*70 + "\n")
