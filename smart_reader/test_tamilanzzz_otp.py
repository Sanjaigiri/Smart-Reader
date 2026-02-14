"""
Test OTP Sending to tamilanzzz001@gmail.com
Verifies delivery within 20 seconds
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.conf import settings
from reader.models import OTPVerification
from reader.views import send_otp_email
from django.utils import timezone
from datetime import timedelta
import time

def test_otp_for_tamilanzzz():
    """Test OTP sending to tamilanzzz001@gmail.com"""
    test_email = "tamilanzzz001@gmail.com"
    
    print("\n" + "="*80)
    print("🧪 TESTING OTP FOR tamilanzzz001@gmail.com")
    print("="*80)
    print(f"📧 Target Email: {test_email}")
    print(f"⏱️  Timeout: 20 seconds")
    print(f"🔧 USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
    print(f"📮 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print("="*80)
    
    # Check if App Password is set
    email_password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
    if not email_password or email_password == 'YOUR_APP_PASSWORD_HERE':
        print("\n⚠️  APP PASSWORD NOT SET!")
        print("="*80)
        print("\n📝 To enable real email sending:")
        print("   1. Get Gmail App Password: https://myaccount.google.com/apppasswords")
        print("   2. Update .env file:")
        print("      EMAIL_HOST_PASSWORD=your-16-char-password")
        print("   3. Save and restart server")
        print("\n💡 Current mode: CONSOLE (OTP in terminal)")
        print("="*80)
    
    # Generate OTP
    print(f"\n🔐 Generating OTP...")
    otp = OTPVerification.generate_otp()
    print(f"   ✓ OTP: {otp}")
    
    # Clean old records
    OTPVerification.objects.filter(email=test_email).delete()
    
    # Save to database
    expires_at = timezone.now() + timedelta(minutes=10)
    OTPVerification.objects.create(
        email=test_email,
        otp=otp,
        expires_at=expires_at
    )
    print(f"   ✓ Saved to database")
    
    # Send OTP
    print(f"\n📧 Sending OTP to {test_email}...")
    print(f"   ⏱️  Max wait time: 20 seconds")
    
    start_time = time.time()
    success = send_otp_email(test_email, otp)
    elapsed = time.time() - start_time
    
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    print(f"Time: {elapsed:.2f} seconds")
    print(f"Within 20s: {'✅ YES' if elapsed <= 20 else '❌ NO'}")
    
    if success:
        if getattr(settings, 'USE_REAL_EMAIL', False):
            print(f"\n📬 CHECK YOUR EMAIL INBOX!")
            print(f"   Email: {test_email}")
            print(f"   Subject: SmartReader - Email Verification OTP")
            print(f"   OTP: {otp}")
            print(f"\n💡 Also check spam folder")
        else:
            print(f"\n📺 CONSOLE MODE")
            print(f"   OTP printed in terminal above")
            print(f"   OTP: {otp}")
    
    print("="*80)
    
    return success, elapsed

if __name__ == "__main__":
    try:
        success, elapsed = test_otp_for_tamilanzzz()
        
        if success and elapsed <= 20:
            print("\n✅ Test PASSED! OTP sent within 20 seconds!")
        elif success:
            print(f"\n⚠️  Test SLOW: Took {elapsed:.2f} seconds (> 20s)")
        else:
            print("\n❌ Test FAILED")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
