#!/usr/bin/env python
"""
Quick OTP Test Script
=====================
Tests the OTP functionality with console mode
"""

import requests
import json
import time

print("\n" + "="*70)
print("🧪 TESTING OTP FUNCTIONALITY")
print("="*70)

# Test email
test_email = "harishoffil5@gmail.com"

print(f"\n📧 Testing with email: {test_email}")
print("⏳ Sending OTP request...\n")

try:
    # Send OTP request
    response = requests.post(
        'http://127.0.0.1:8000/send-otp/',
        data=json.dumps({'email': test_email}),
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    result = response.json()
    
    print("="*70)
    print("📬 RESPONSE FROM SERVER:")
    print("="*70)
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('message')}")
    
    if result.get('debug_otp'):
        print(f"\n🔐 OTP Code: {result.get('debug_otp')}")
        print("   ⚠️  This OTP is shown because you're in CONSOLE MODE")
        print("   ℹ️  Check the Django terminal for the full OTP output")
    
    print("="*70)
    
    if result.get('status') == 'success':
        print("\n✅ SUCCESS! OTP generation is working!")
        print("\n📋 What happens in CONSOLE MODE:")
        print("   1. OTP is generated and saved to database ✓")
        print("   2. OTP is printed in the Django server terminal ✓")
        print("   3. No actual email is sent (testing mode) ✓")
        
        print("\n🔄 TO ENABLE REAL EMAIL SENDING:")
        print("   1. Go to: https://myaccount.google.com/apppasswords")
        print("   2. Sign in with: harishoffil5@gmail.com")
        print("   3. Create App Password (16 characters)")
        print("   4. Update .env file:")
        print("      EMAIL_HOST_PASSWORD=your-16-char-password")
        print("      USE_REAL_EMAIL=True")
        print("   5. Restart Django server")
        
    else:
        print("\n❌ ERROR! Something went wrong.")
        print(f"   Error message: {result.get('message')}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to Django server!")
    print("   Make sure the server is running at: http://127.0.0.1:8000/")
    print("   Run: python manage.py runserver")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("🎯 TEST COMPLETE")
print("="*70 + "\n")
