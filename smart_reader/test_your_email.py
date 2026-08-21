import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

print("\n" + "="*70)
print("📧 TESTING OTP EMAIL WITH YOUR CREDENTIALS")
print("="*70)

print(f"\n📋 Testing with:")
print(f"  Email: tamilanzzz001@gmail.com")
print(f"  Password: sanjai giri 123 (formatted as: sanjaigiri123)")

test_otp = '987654'
test_email = 'tamilanzzz001@gmail.com'

subject = 'SmartReader - OTP Verification Test'
message = f'''Hello!

Your OTP for SmartReader is: {test_otp}

This is a test to verify email configuration is working.

Best regards,
SmartReader Team
'''

html_message = f'''
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <div style="max-width: 500px; margin: 0 auto; background: #f9fafb; padding: 30px; border-radius: 10px;">
        <h2 style="color: #6366f1; text-align: center;">📚 SmartReader</h2>
        <p>Hello!</p>
        <p>Your OTP for email verification is:</p>
        <div style="background: #6366f1; color: white; font-size: 32px; font-weight: bold; text-align: center; padding: 20px; border-radius: 8px; letter-spacing: 8px; margin: 20px 0;">
            {test_otp}
        </div>
        <p style="color: #666;">This OTP will expire in <strong>10 minutes</strong>.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">SmartReader Team</p>
    </div>
</body>
</html>
'''

print(f"\n🔄 Attempting to send OTP to: {test_email}")

try:
    email_msg = EmailMultiAlternatives(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [test_email]
    )
    email_msg.attach_alternative(html_message, "text/html")
    result = email_msg.send(fail_silently=False)
    
    print(f"\n✅✅✅ SUCCESS! Email sent successfully! ✅✅✅")
    print(f"\n📧 CHECK YOUR INBOX: {test_email}")
    print(f"   Test OTP sent: {test_otp}")
    print(f"\n🎉 GREAT NEWS! OTP emails are working 100% correctly!")
    print(f"\n📱 Now you can:")
    print(f"   1. Go to signup page")
    print(f"   2. Enter your email: {test_email}")
    print(f"   3. Click 'Send OTP'")
    print(f"   4. Check your Gmail inbox for OTP")
    print(f"   5. Enter OTP and complete registration")
    print(f"\n✅ Everything is working perfectly!")
    
except Exception as e:
    error_msg = str(e)
    print(f"\n❌ ERROR: Cannot send email with regular Gmail password!")
    print(f"\nError message: {error_msg}")
    
    if "Username and Password not accepted" in error_msg or "535" in error_msg:
        print(f"\n" + "="*70)
        print(f"⚠️  PROBLEM: Regular Gmail Password Won't Work!")
        print(f"="*70)
        print(f"\nGmail blocks regular passwords for security reasons.")
        print(f"You need to generate an 'App Password' instead.")
        print(f"\n🔧 HOW TO FIX (Takes 2 minutes):")
        print(f"\n1️⃣  Go to Google Account:")
        print(f"    https://myaccount.google.com/apppasswords")
        print(f"\n2️⃣  Sign in with:")
        print(f"    Email: tamilanzzz001@gmail.com")
        print(f"    Password: sanjai giri 123")
        print(f"\n3️⃣  Create App Password:")
        print(f"    - Click 'Select app' → Choose 'Mail'")
        print(f"    - Click 'Select device' → Choose 'Other'")
        print(f"    - Type name: 'SmartReader'")
        print(f"    - Click 'Generate'")
        print(f"\n4️⃣  Copy the 16-character password:")
        print(f"    Example: 'abcd efgh ijkl mnop'")
        print(f"    Remove spaces → 'abcdefghijklmnop'")
        print(f"\n5️⃣  Send me that 16-character password")
        print(f"    I'll update the .env file and test again!")
        print(f"\n💡 NOTE:")
        print(f"   - App Password is different from your Gmail password")
        print(f"   - It's a special password just for apps")
        print(f"   - More secure than using your real password")
        print(f"   - You can revoke it anytime from Google settings")
        
    else:
        print(f"\n🔧 Other issue detected. Full error:")
        import traceback
        traceback.print_exc()

print("\n" + "="*70 + "\n")
