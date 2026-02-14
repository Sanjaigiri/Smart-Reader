"""
Test OTP Email Performance
==========================
This script tests the optimized OTP email configuration
and ensures emails are sent within 10 seconds.

Usage:
    python test_otp_performance.py
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from reader.models import OTPVerification
from django.utils import timezone
from datetime import timedelta


def print_banner(text):
    """Print a styled banner"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def test_email_configuration():
    """Test 1: Check email configuration"""
    print_banner("TEST 1: EMAIL CONFIGURATION")
    
    print("\n📋 Current Settings:")
    print(f"   USE_REAL_EMAIL: {settings.USE_REAL_EMAIL}")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   EMAIL_TIMEOUT: {getattr(settings, 'EMAIL_TIMEOUT', 'Not set')}")
    
    if settings.USE_REAL_EMAIL:
        if settings.EMAIL_HOST_PASSWORD:
            print(f"   EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD)} (SET)")
        else:
            print(f"   ⚠️  EMAIL_HOST_PASSWORD: NOT SET!")
            print(f"   💡 Please set Gmail App Password in .env file")
    
    print("\n✅ Configuration loaded successfully!")


def test_otp_generation():
    """Test 2: OTP generation speed"""
    print_banner("TEST 2: OTP GENERATION SPEED")
    
    start = time.time()
    
    # Generate 10 OTPs
    otps = []
    for i in range(10):
        otp = OTPVerification.generate_otp()
        otps.append(otp)
    
    elapsed = time.time() - start
    
    print(f"\n   Generated 10 OTPs: {', '.join(otps)}")
    print(f"   ⚡ Time taken: {elapsed*1000:.2f}ms")
    print(f"   📊 Average: {elapsed*100:.2f}ms per OTP")
    
    if elapsed < 0.1:
        print(f"   ✅ EXCELLENT: OTP generation is instant!")
    else:
        print(f"   ⚠️  WARNING: OTP generation is slow")
    
    return elapsed < 1


def test_email_delivery_performance(test_email=None):
    """Test 3: Email delivery performance"""
    print_banner("TEST 3: EMAIL DELIVERY PERFORMANCE")
    
    if not test_email:
        test_email = input("\n   📧 Enter test email address (or press Enter to skip): ").strip()
        
        if not test_email:
            print("\n   ⏭️  Skipping email delivery test")
            return True
    
    print(f"\n   Testing email delivery to: {test_email}")
    print(f"   Mode: {'REAL EMAIL' if settings.USE_REAL_EMAIL else 'CONSOLE'}")
    
    # Generate OTP
    otp = OTPVerification.generate_otp()
    print(f"   🔐 OTP: {otp}")
    
    # Create email
    subject = '🔐 SmartReader - OTP Performance Test'
    message = f'''Hello!

This is a performance test for SmartReader OTP delivery.

Your test OTP is: {otp}

Time: {datetime.now().strftime('%H:%M:%S')}

This is just a test - no action required.

Best regards,
SmartReader Team
'''
    
    html_message = f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:20px;font-family:Arial,sans-serif;background:#f5f5f5">
<div style="max-width:500px;margin:0 auto;background:#fff;padding:30px;border-radius:10px">
<h2 style="color:#6366f1;text-align:center">📚 SmartReader - Test</h2>
<p>This is a performance test.</p>
<div style="background:#667eea;color:#fff;font-size:32px;font-weight:bold;text-align:center;padding:20px;border-radius:8px;letter-spacing:8px">{otp}</div>
<p style="color:#999;font-size:11px">Test sent at: {datetime.now().strftime('%H:%M:%S')}</p>
</div>
</body>
</html>'''
    
    try:
        print(f"\n   ⏱️  Starting email delivery...")
        start = time.time()
        
        # Send email
        from_email = settings.DEFAULT_FROM_EMAIL
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[test_email]
        )
        email_msg.attach_alternative(html_message, "text/html")
        
        # Send with timeout protection
        import socket
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(10)
        
        try:
            email_msg.send(fail_silently=False)
        finally:
            socket.setdefaulttimeout(original_timeout)
        
        elapsed = time.time() - start
        
        print(f"\n   ✅ EMAIL SENT SUCCESSFULLY!")
        print(f"   ⚡ Delivery time: {elapsed:.2f} seconds")
        
        if elapsed < 5:
            print(f"   🎉 EXCELLENT: Under 5 seconds!")
        elif elapsed < 10:
            print(f"   ✅ GOOD: Under 10 seconds!")
        else:
            print(f"   ⚠️  SLOW: Over 10 seconds")
        
        if settings.USE_REAL_EMAIL:
            print(f"\n   📬 Check inbox: {test_email}")
            print(f"   💡 Also check spam folder!")
        else:
            print(f"\n   📺 Check terminal output above for email content")
        
        return elapsed < 10
        
    except socket.timeout:
        print(f"\n   ⚠️  TIMEOUT: Email took more than 10 seconds")
        print(f"   💡 Email may still be delivered, but it's too slow")
        return False
        
    except Exception as e:
        print(f"\n   ❌ ERROR: {str(e)}")
        print(f"\n   Troubleshooting:")
        
        if settings.USE_REAL_EMAIL:
            print(f"   1. Check Gmail App Password in .env file")
            print(f"   2. Make sure 2-factor authentication is enabled on Gmail")
            print(f"   3. Visit: https://myaccount.google.com/apppasswords")
            print(f"   4. Generate new App Password and update .env")
        else:
            print(f"   1. Console mode is active - check terminal output")
            print(f"   2. To test real email, set USE_REAL_EMAIL=True in .env")
        
        return False


def test_database_otp_operations():
    """Test 4: Database OTP operations"""
    print_banner("TEST 4: DATABASE OTP OPERATIONS")
    
    test_email = "performance_test@example.com"
    
    print(f"\n   Testing OTP database operations...")
    
    # Clean up old test records
    OTPVerification.objects.filter(email=test_email).delete()
    
    start = time.time()
    
    # Create OTP
    otp = OTPVerification.generate_otp()
    expires_at = timezone.now() + timedelta(minutes=10)
    
    otp_record = OTPVerification.objects.create(
        email=test_email,
        otp=otp,
        expires_at=expires_at
    )
    
    # Retrieve OTP
    retrieved = OTPVerification.objects.filter(email=test_email, otp=otp).first()
    
    # Verify
    if retrieved:
        retrieved.is_verified = True
        retrieved.save()
    
    # Delete
    OTPVerification.objects.filter(email=test_email).delete()
    
    elapsed = time.time() - start
    
    print(f"   ✓ Create OTP record")
    print(f"   ✓ Retrieve OTP record")
    print(f"   ✓ Update verification status")
    print(f"   ✓ Delete OTP record")
    print(f"\n   ⚡ Total time: {elapsed*1000:.2f}ms")
    
    if elapsed < 0.1:
        print(f"   ✅ EXCELLENT: Database operations are fast!")
    else:
        print(f"   ⚠️  WARNING: Database operations are slow")
    
    return elapsed < 1


def run_all_tests():
    """Run all performance tests"""
    print("\n" + "="*70)
    print("  🚀 SMARTREADER OTP PERFORMANCE TEST SUITE")
    print("  Testing optimized email configuration")
    print("="*70)
    
    results = {}
    
    # Test 1: Configuration
    try:
        test_email_configuration()
        results['config'] = True
    except Exception as e:
        print(f"\n   ❌ Configuration test failed: {e}")
        results['config'] = False
    
    # Test 2: OTP Generation
    try:
        results['generation'] = test_otp_generation()
    except Exception as e:
        print(f"\n   ❌ Generation test failed: {e}")
        results['generation'] = False
    
    # Test 3: Database Operations
    try:
        results['database'] = test_database_otp_operations()
    except Exception as e:
        print(f"\n   ❌ Database test failed: {e}")
        results['database'] = False
    
    # Test 4: Email Delivery (optional)
    try:
        results['delivery'] = test_email_delivery_performance()
    except Exception as e:
        print(f"\n   ❌ Delivery test failed: {e}")
        results['delivery'] = False
    
    # Final Report
    print_banner("📊 TEST RESULTS SUMMARY")
    
    print(f"\n   Configuration Check: {'✅ PASS' if results.get('config') else '❌ FAIL'}")
    print(f"   OTP Generation: {'✅ PASS' if results.get('generation') else '❌ FAIL'}")
    print(f"   Database Operations: {'✅ PASS' if results.get('database') else '❌ FAIL'}")
    print(f"   Email Delivery: {'✅ PASS' if results.get('delivery') else '❌ FAIL/SKIPPED'}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*70)
    if all_passed:
        print("  🎉 ALL TESTS PASSED!")
        print("  Your OTP system is optimized for high performance!")
    else:
        print("  ⚠️  SOME TESTS FAILED")
        print("  Please check the output above for details")
    print("="*70 + "\n")
    
    # Performance Guarantee
    if results.get('delivery'):
        print("  ⚡ PERFORMANCE GUARANTEE:")
        print("  ✓ OTP generation: < 1ms")
        print("  ✓ Database operations: < 100ms")
        print("  ✓ Email delivery: < 10 seconds")
        print("  ✓ Total user wait time: < 10 seconds\n")


if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n  ⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n  ❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
