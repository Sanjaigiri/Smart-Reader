import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

print("\n" + "="*60)
print("📧 TESTING OTP EMAIL TO: tamilanzzz001@gmail.com")
print("="*60)

print("\n📋 Email Configuration:")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
print(f"  EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
print(f"  EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
print(f"  EMAIL_HOST_PASSWORD: {'SET (' + str(len(settings.EMAIL_HOST_PASSWORD)) + ' chars)' if getattr(settings, 'EMAIL_HOST_PASSWORD', '') else 'NOT SET'}")

# Generate test OTP
test_otp = '123456'
test_email = 'tamilanzzz001@gmail.com'

subject = 'SmartReader - Test OTP Email'
message = f'''Hello!

This is a TEST OTP from SmartReader.

Your OTP is: {test_otp}

If you received this email, the OTP system is working correctly!

Best regards,
SmartReader Team
'''

html_message = f'''
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="max-width: 500px; margin: 0 auto; background: #f9fafb; padding: 30px; border-radius: 10px;">
        <h2 style="color: #6366f1; text-align: center;">📚 SmartReader - Test Email</h2>
        <p>Hello!</p>
        <p>This is a <strong>TEST OTP</strong> email.</p>
        <div style="background: #6366f1; color: white; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 8px; letter-spacing: 8px; margin: 20px 0;">
            {test_otp}
        </div>
        <p style="color: #10b981; font-weight: bold;">✅ If you received this, OTP emails are working!</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">SmartReader Team</p>
    </div>
</body>
</html>
'''

print(f"\n🔄 Sending test email to: {test_email}")
print(f"   Test OTP: {test_otp}")

try:
    email_msg = EmailMultiAlternatives(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [test_email]
    )
    email_msg.attach_alternative(html_message, "text/html")
    result = email_msg.send(fail_silently=False)
    
    print(f"\n✅ SUCCESS! Email sent successfully!")
    print(f"   Result: {result} email(s) sent")
    print(f"\n📧 Please check the inbox of: {test_email}")
    print(f"   Also check SPAM/JUNK folder!")
    print(f"   Test OTP: {test_otp}")
    
except Exception as e:
    print(f"\n❌ ERROR sending email!")
    print(f"   Error: {str(e)}")
    print(f"\n🔧 Troubleshooting:")
    print(f"   1. Check if EMAIL_HOST_PASSWORD is correct in .env")
    print(f"   2. Make sure Gmail App Password is valid")
    print(f"   3. Check if 2FA is enabled on Gmail")
    print(f"   4. Try generating new App Password")
    
    import traceback
    print(f"\n📋 Full error:")
    traceback.print_exc()

print("\n" + "="*60 + "\n")
