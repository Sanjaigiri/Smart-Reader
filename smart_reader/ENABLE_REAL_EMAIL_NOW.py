"""
QUICK SETUP: Enable Real Email for sriakilkaviraj2005@gmail.com
Run this script to configure Gmail and send a test OTP
"""
import os

print("\n" + "="*70)
print("📧 ENABLE REAL EMAIL SENDING FOR: sriakilkaviraj2005@gmail.com")
print("="*70)

print("\n🔐 IMPORTANT: You need a Gmail App Password to send real emails")
print("\n📋 How to Get Gmail App Password:")
print("   1. Open: https://myaccount.google.com/apppasswords")
print("   2. Sign in with: sriakilkaviraj2005@gmail.com")
print("   3. Enable 2-Step Verification (required)")
print("      Link: https://myaccount.google.com/security")
print("   4. Go back to App Passwords page")
print("   5. Create new App Password:")
print("      - App name: SmartReader")
print("      - Click 'Create'")
print("   6. Copy the 16-character password")
print("      Example: abcd efgh ijkl mnop")
print("   7. Remove spaces: abcdefghijklmnop")

print("\n" + "-"*70)
print("\n⚠️  Security Note:")
print("   - Use APP PASSWORD (16 chars), NOT your regular Gmail password")
print("   - App Password looks like: abcdefghijklmnop")
print("   - Keep it secure, don't share it")

gmail_app_password = input("\n👉 Enter your Gmail App Password (or ENTER to skip): ").strip()

# Remove spaces from password
gmail_app_password = gmail_app_password.replace(' ', '')

if not gmail_app_password:
    print("\n⏭️  Skipped. You can run this script again later.")
    print("   To test OTP now, check the server terminal for OTP codes.")
    exit(0)

if len(gmail_app_password) != 16:
    print(f"\n❌ ERROR: App Password should be 16 characters (you entered {len(gmail_app_password)})")
    print("   Example of correct format: abcdefghijklmnop")
    print("\n💡 Tips:")
    print("   - Remove all spaces from the password")
    print("   - Make sure you copied the entire password")
    print("   - Get new App Password if needed")
    exit(1)

print(f"\n✅ Password received ({len(gmail_app_password)} characters)")
print("   Updating configuration...")

# Update .env file
env_path = os.path.join(os.path.dirname(__file__), '.env')

env_content = f"""# Django Settings
SECRET_KEY=7an=(s2w*e5)9=xu_$nyn2mi)ylg7hgs0f@qwjdug^(v9upcs8
DEBUG=True

# ============================================
# EMAIL CONFIGURATION - REAL EMAIL MODE
# ============================================
# Configured for: sriakilkaviraj2005@gmail.com
# Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
# ✅ REAL EMAIL MODE ENABLED
# OTPs will be sent to users' actual email addresses
# Email delivery time: 5-10 seconds
#
# To disable real email (use console mode):
# Change USE_REAL_EMAIL=False

USE_REAL_EMAIL=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sriakilkaviraj2005@gmail.com
EMAIL_HOST_PASSWORD={gmail_app_password}
DEFAULT_FROM_EMAIL=SmartReader <sriakilkaviraj2005@gmail.com>

# Database (SQLite by default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
"""

try:
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ Configuration saved successfully!")
    print(f"   File: {env_path}")
    
except Exception as e:
    print(f"\n❌ Error saving configuration: {e}")
    exit(1)

print("\n" + "="*70)
print("✅ EMAIL CONFIGURATION COMPLETE!")
print("="*70)

print("\n📧 Configuration Details:")
print(f"   Email: sriakilkaviraj2005@gmail.com")
print(f"   Mode: REAL EMAIL SENDING")
print(f"   Password: {'*' * 16} (saved securely)")
print(f"   Status: Ready to send OTPs!")

print("\n📋 NEXT STEPS:")
print("\n   1. RESTART Django Server:")
print("      - Press CTRL+C or CTRL+BREAK to stop current server")
print("      - Run: python manage.py runserver")

print("\n   2. TEST Email Sending:")
print("      - Open new terminal")
print("      - Run: python test_otp_real_email.py")
print("      - This will send test OTP to: sriakilkaviraj2005@gmail.com")

print("\n   3. TRY Signup:")
print("      - Go to: http://127.0.0.1:8000/register/")
print("      - Enter: sriakilkaviraj2005@gmail.com")
print("      - Click: Send OTP")
print("      - CHECK YOUR EMAIL INBOX (and spam folder)")
print("      - OTP will arrive in 5-10 seconds!")

print("\n⏱️  Expected Timing:")
print("   - Click 'Send OTP' → Wait 5-10 seconds → Check email → Done!")

print("\n📬 Email Tips:")
print("   - Check spam/junk folder if not in inbox")
print("   - Add sender to contacts to avoid spam")
print("   - Gmail may filter first email as spam")

print("\n🎉 Your SmartReader project is ready for real OTP emails!")
print("="*70 + "\n")
