import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from reader.models import OTPVerification
from django.conf import settings

print("\n" + "="*70)
print("📊 OTP SYSTEM STATUS CHECK")
print("="*70)

# Email Configuration
print("\n📋 Email Configuration:")
print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"  USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
if hasattr(settings, 'EMAIL_HOST'):
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
if hasattr(settings, 'EMAIL_HOST_USER'):
    print(f"  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")

# OTP Records
print(f"\n📧 OTP Records in Database:")
print(f"  Total OTP Records: {OTPVerification.objects.count()}")

if OTPVerification.objects.exists():
    print("\n  Recent OTPs (Last 10):")
    for otp in OTPVerification.objects.all()[:10]:
        status = "✅ Verified" if otp.is_verified else "⏳ Pending"
        expired = "❌ Expired" if otp.is_expired() else "✓ Valid"
        print(f"    • {otp.email}")
        print(f"      OTP: {otp.otp} | {status} | {expired}")
        print(f"      Created: {otp.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
else:
    print("  ℹ️ No OTP records found")

print("\n" + "="*70)
print("✅ OTP SYSTEM STATUS:")
if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
    print("  📝 Mode: CONSOLE (OTPs printed in terminal)")
    print("  ⚠️ Real emails will NOT be sent")
    print("  💡 To send real emails, set USE_REAL_EMAIL=True in .env")
else:
    print("  📧 Mode: REAL EMAIL (OTPs sent to actual email addresses)")
    print("  ✅ OTP emails are being sent!")
print("="*70 + "\n")
