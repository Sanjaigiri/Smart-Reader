"""
Test Real Email Sending - After App Password Setup
Run this after you've added your Gmail App Password to .env file
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from reader.views import send_otp_email
from reader.models import OTPVerification
from django.utils import timezone
from datetime import timedelta

def test_email_config():
    """Test email configuration"""
    print("\n" + "="*80)
    print("📧 TESTING REAL EMAIL CONFIGURATION")
    print("="*80)
    
    print("\n🔍 Checking Configuration...")
    print(f"   USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"   EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"   EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    
    # Check if App Password is set
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    if not email_password or email_password == 'YOUR_APP_PASSWORD_HERE':
        print("\n" + "="*80)
        print("⚠️  APP PASSWORD NOT SET!")
        print("="*80)
        print("\n❌ You need to add your Gmail App Password to .env file")
        print("\n📝 Follow these steps:")
        print("   1. Get App Password: https://myaccount.google.com/apppasswords")
        print("   2. Edit file: d:\\Django\\Final_Sem\\smart_reader\\.env")
        print("   3. Replace YOUR_APP_PASSWORD_HERE with your password (no spaces)")
        print("   4. Save file and run this test again")
        print("\n💡 See GET_GMAIL_APP_PASSWORD.md for detailed instructions")
        print("="*80)
        return False
    
    print(f"   EMAIL_HOST_PASSWORD: {'*' * 16} (Set ✓)")
    
    return True

def send_test_otp():
    """Send test OTP to the email"""
    test_email = "sanjaigiri001@gmail.com"
    
    print("\n" + "="*80)
    print("📨 SENDING TEST OTP EMAIL")
    print("="*80)
    print(f"   Target: {test_email}")
    
    # Generate OTP
    otp = OTPVerification.generate_otp()
    print(f"   OTP: {otp}")
    
    # Save to database
    OTPVerification.objects.filter(email=test_email).delete()
    expires_at = timezone.now() + timedelta(minutes=10)
    OTPVerification.objects.create(
        email=test_email,
        otp=otp,
        expires_at=expires_at
    )
    print(f"   ✓ Saved to database")
    
    # Send email
    print(f"\n   📧 Sending email...")
    import time
    start = time.time()
    
    try:
        success = send_otp_email(test_email, otp)
        elapsed = time.time() - start
        
        if success:
            print(f"\n✅ EMAIL SENT SUCCESSFULLY!")
            print(f"   ⏱️  Time: {elapsed:.2f} seconds")
            print(f"\n📬 CHECK YOUR EMAIL INBOX!")
            print(f"   Email: {test_email}")
            print(f"   Subject: 🔐 SmartReader - Email Verification OTP")
            print(f"   OTP: {otp}")
            print(f"\n💡 Also check your spam folder if not in inbox")
            return True
        else:
            print(f"\n❌ Failed to send email")
            print(f"   Time taken: {elapsed:.2f} seconds")
            return False
            
    except Exception as e:
        elapsed = time.time() - start
        print(f"\n❌ ERROR SENDING EMAIL!")
        print(f"   Error: {e}")
        print(f"   Time: {elapsed:.2f} seconds")
        
        if "authentication" in str(e).lower() or "credentials" in str(e).lower():
            print(f"\n⚠️  AUTHENTICATION ERROR!")
            print(f"   This means your Gmail App Password is incorrect")
            print(f"\n📝 Solutions:")
            print(f"   1. Check if you removed all spaces from the password")
            print(f"   2. Verify the password is exactly 16 characters")
            print(f"   3. Generate a new App Password")
            print(f"   4. Update .env file with correct password")
        
        return False

def main():
    print("\n" + "="*80)
    print("🧪 GMAIL APP PASSWORD TEST")
    print("="*80)
    print("This will test if your Gmail App Password is configured correctly")
    print("="*80)
    
    # Check configuration
    if not test_email_config():
        print("\n❌ Configuration incomplete. Please set up App Password first.")
        return
    
    print("\n✅ Configuration looks good!")
    
    # Ask for confirmation
    print("\n" + "="*80)
    print("📧 Ready to send test OTP email to: sanjaigiri001@gmail.com")
    print("="*80)
    
    # Send test email
    success = send_test_otp()
    
    print("\n" + "="*80)
    if success:
        print("✅ TEST SUCCESSFUL!")
        print("="*80)
        print("\nYour email configuration is working perfectly!")
        print("You can now use the signup page and receive OTP in your email.")
        print("\n🚀 Next Steps:")
        print("   1. Go to: http://127.0.0.1:8000/register/")
        print("   2. Enter email: sanjaigiri001@gmail.com")
        print("   3. Click 'Send OTP'")
        print("   4. Check your email inbox (and spam folder)")
        print("   5. Enter the OTP to verify")
    else:
        print("❌ TEST FAILED")
        print("="*80)
        print("\nPlease check:")
        print("   1. Gmail App Password is correct in .env file")
        print("   2. No spaces in the password")
        print("   3. 2-Step Verification is enabled on your Gmail")
        print("   4. Django server terminal for detailed error messages")
        print("\n💡 See GET_GMAIL_APP_PASSWORD.md for help")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
