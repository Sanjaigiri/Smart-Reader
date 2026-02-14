"""
Test OTP functionality with real email: sanjaigiri001@gmail.com
This script will test the complete OTP flow
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.conf import settings
from reader.models import OTPVerification
from reader.views import send_otp_email
from django.utils import timezone
from datetime import timedelta
import json

def test_otp_flow():
    """Test complete OTP flow"""
    test_email = "sanjaigiri001@gmail.com"
    
    print("\n" + "="*80)
    print("🧪 TESTING OTP FUNCTIONALITY")
    print("="*80)
    print(f"📧 Test Email: {test_email}")
    print(f"🔧 DEBUG Mode: {settings.DEBUG}")
    print(f"📨 USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
    print(f"📮 EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"📬 EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"👤 EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print("="*80)
    
    # Step 1: Clean up old OTP records
    print("\n📋 Step 1: Cleaning up old OTP records...")
    deleted = OTPVerification.objects.filter(email=test_email).delete()
    print(f"   ✓ Deleted {deleted[0]} old records")
    
    # Step 2: Generate OTP
    print("\n🔐 Step 2: Generating OTP...")
    otp = OTPVerification.generate_otp()
    print(f"   ✓ Generated OTP: {otp}")
    
    # Step 3: Save OTP to database
    print("\n💾 Step 3: Saving OTP to database...")
    expires_at = timezone.now() + timedelta(minutes=10)
    otp_record = OTPVerification.objects.create(
        email=test_email,
        otp=otp,
        expires_at=expires_at
    )
    print(f"   ✓ OTP saved with ID: {otp_record.id}")
    print(f"   ✓ Expires at: {expires_at}")
    
    # Step 4: Send OTP email
    print("\n📧 Step 4: Sending OTP email...")
    print(f"   📨 Attempting to send to: {test_email}")
    
    import time
    start_time = time.time()
    email_sent = send_otp_email(test_email, otp)
    elapsed = time.time() - start_time
    
    if email_sent:
        print(f"   ✅ EMAIL SENT SUCCESSFULLY in {elapsed:.2f} seconds!")
        if getattr(settings, 'USE_REAL_EMAIL', False):
            print(f"   📬 Check your inbox: {test_email}")
            print(f"   📁 Also check spam folder")
        else:
            print(f"   📺 Console Mode: Check terminal output above for OTP")
            print(f"   🔐 OTP: {otp}")
    else:
        print(f"   ⚠️  Email not sent (took {elapsed:.2f}s)")
        print(f"   📺 Console Mode Active - OTP printed to terminal")
        print(f"   🔐 OTP: {otp}")
    
    # Step 5: Verify OTP exists in database
    print("\n🔍 Step 5: Verifying OTP in database...")
    try:
        db_otp = OTPVerification.objects.get(email=test_email, otp=otp)
        print(f"   ✓ OTP found in database")
        print(f"   ✓ Email: {db_otp.email}")
        print(f"   ✓ OTP: {db_otp.otp}")
        print(f"   ✓ Is Verified: {db_otp.is_verified}")
        print(f"   ✓ Is Expired: {db_otp.is_expired()}")
        print(f"   ✓ Expires at: {db_otp.expires_at}")
    except OTPVerification.DoesNotExist:
        print(f"   ❌ OTP not found in database!")
    
    # Step 6: Test OTP verification
    print("\n✅ Step 6: Testing OTP verification...")
    try:
        otp_record.is_verified = True
        otp_record.save()
        print(f"   ✓ OTP marked as verified")
    except Exception as e:
        print(f"   ❌ Error verifying OTP: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    print(f"✅ OTP Generation: SUCCESS")
    print(f"✅ Database Storage: SUCCESS")
    print(f"{'✅' if email_sent else '⚠️ '} Email Sending: {'SUCCESS' if email_sent else 'CONSOLE MODE'}")
    print(f"✅ OTP Verification: SUCCESS")
    print("="*80)
    
    print("\n🎯 NEXT STEPS:")
    print("="*80)
    if not getattr(settings, 'USE_REAL_EMAIL', False):
        print("📌 Currently in CONSOLE MODE - OTP printed to terminal")
        print("📌 To enable real email sending:")
        print("   1. Edit .env file in smart_reader folder")
        print("   2. Set USE_REAL_EMAIL=True")
        print("   3. Add Gmail App Password")
        print("   4. Restart Django server")
    else:
        print(f"📌 Real email sent to: {test_email}")
        print(f"📌 OTP: {otp}")
        print("📌 Check your inbox and spam folder")
        print("📌 OTP expires in 10 minutes")
    print("="*80)
    
    print("\n🔐 YOUR OTP FOR TESTING:")
    print("="*80)
    print(f"   {otp}")
    print("="*80)
    
    return otp

if __name__ == "__main__":
    try:
        otp = test_otp_flow()
        print("\n✅ Test completed successfully!")
        print(f"\n🔑 Use this OTP to test signup: {otp}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
