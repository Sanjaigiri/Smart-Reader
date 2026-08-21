"""
AUTOMATIC EMAIL CONFIGURATION FOR sriakilkaviraj2005@gmail.com
This script will update your .env file to enable real email sending
"""
import os
from datetime import datetime

print("\n" + "="*70)
print("📧 CONFIGURING EMAIL FOR: sriakilkaviraj2005@gmail.com")
print("="*70)

print("\n🔐 To send real OTP emails, you need a Gmail App Password.")
print("\n📋 How to get Gmail App Password:")
print("   1. Visit: https://myaccount.google.com/apppasswords")
print("   2. Sign in with: sriakilkaviraj2005@gmail.com")
print("   3. Make sure 2-Step Verification is enabled")
print("   4. Create new App Password named 'SmartReader'")
print("   5. Copy the 16-character password (spaces will be removed)")

print("\n" + "-"*70)
gmail_password = input("\n👉 Enter your Gmail App Password (or press Enter to skip): ").strip()

# Remove spaces from password
gmail_password = gmail_password.replace(' ', '')

env_path = os.path.join(os.path.dirname(__file__), '.env')

if not gmail_password or len(gmail_password) != 16:
    print("\n⚠️  No valid App Password provided.")
    print("   Keeping console mode (OTPs will be printed to terminal)")
    
    env_content = f"""# Django Settings
SECRET_KEY=7an=(s2w*e5)9=xu_$nyn2mi)ylg7hgs0f@qwjdug^(v9upcs8
DEBUG=True

# ============================================
# EMAIL CONFIGURATION FOR OTP SENDING
# ============================================
# Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
# MODE: CONSOLE MODE (Development/Testing)
# - OTPs are printed to server terminal/console
# - Perfect for testing without email setup
# - User can see OTP in terminal output
#
# TO ENABLE REAL EMAIL SENDING:
# 1. Get Gmail App Password: https://myaccount.google.com/apppasswords
# 2. Run: python configure_email.py
# 3. Or manually edit this file and set:
#    USE_REAL_EMAIL=True
#    EMAIL_HOST_USER=sriakilkaviraj2005@gmail.com
#    EMAIL_HOST_PASSWORD=your_16_char_app_password

USE_REAL_EMAIL=False
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sriakilkaviraj2005@gmail.com
EMAIL_HOST_PASSWORD=WAITING_FOR_APP_PASSWORD
DEFAULT_FROM_EMAIL=SmartReader <sriakilkaviraj2005@gmail.com>

# Database (SQLite by default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
"""
    
    mode = "CONSOLE MODE"
    
else:
    print(f"\n✅ Gmail App Password received ({len(gmail_password)} characters)")
    print("   Configuring for REAL EMAIL SENDING...")
    
    env_content = f"""# Django Settings
SECRET_KEY=7an=(s2w*e5)9=xu_$nyn2mi)ylg7hgs0f@qwjdug^(v9upcs8
DEBUG=True

# ============================================
# EMAIL CONFIGURATION FOR OTP SENDING
# ============================================
# Configured: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
# MODE: REAL EMAIL SENDING (Production Ready!)
# - OTPs are sent to users' actual email addresses
# - Uses Gmail SMTP with App Password
# - Perfect for final year project demonstration
#
# Email: sriakilkaviraj2005@gmail.com
# App Password: Configured securely
#
# ⚠️  SECURITY: Never share your App Password or commit it to Git!

USE_REAL_EMAIL=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=sriakilkaviraj2005@gmail.com
EMAIL_HOST_PASSWORD={gmail_password}
DEFAULT_FROM_EMAIL=SmartReader <sriakilkaviraj2005@gmail.com>

# Database (SQLite by default)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
"""
    
    mode = "REAL EMAIL MODE"

# Save configuration
try:
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved to: {env_path}")
    print(f"📧 Mode: {mode}")
    
except Exception as e:
    print(f"\n❌ Error saving configuration: {e}")
    exit(1)

print("\n" + "="*70)
print("✅ CONFIGURATION COMPLETE!")
print("="*70)

if gmail_password and len(gmail_password) == 16:
    print("\n📧 Email Configuration:")
    print(f"   Email: sriakilkaviraj2005@gmail.com")
    print(f"   Mode: REAL EMAIL SENDING")
    print(f"   Status: Ready to send OTPs to real email addresses")
    
    print("\n📋 Next Steps:")
    print("   1. RESTART Django server (CTRL+C then run again)")
    print("      cd D:\\Django\\Final_Sem\\smart_reader")
    print("      python manage.py runserver")
    print("\n   2. TEST email sending:")
    print("      python test_otp_real_email.py")
    print("\n   3. Try signup with real OTP:")
    print("      - Go to: http://127.0.0.1:8000/register/")
    print("      - Enter: sriakilkaviraj2005@gmail.com")
    print("      - Click: Send OTP")
    print("      - Check: Email inbox (and spam folder)")
    print("      - OTP should arrive in 5-10 seconds!")
    
    print("\n⏱️  OTP Timing:")
    print("   - OTP generation: Instant")
    print("   - Email sending: 5-10 seconds")
    print("   - Total time: ~10 seconds")
    
else:
    print("\n📧 Email Configuration:")
    print(f"   Mode: CONSOLE MODE (Development)")
    print(f"   Status: OTPs printed to terminal")
    
    print("\n📋 How to Use:")
    print("   1. Go to: http://127.0.0.1:8000/register/")
    print("   2. Enter: sriakilkaviraj2005@gmail.com")
    print("   3. Click: Send OTP")
    print("   4. CHECK SERVER TERMINAL for OTP")
    print("   5. Copy OTP from terminal and enter it")
    
    print("\n💡 To Enable Real Emails Later:")
    print("   - Run this script again: python configure_email.py")
    print("   - Provide your Gmail App Password")

print("\n" + "="*70)
print("🎓 Your Final Year Project is Ready!")
print("="*70 + "\n")
