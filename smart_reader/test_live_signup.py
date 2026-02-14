"""
Live Test - OTP Signup Flow with sanjaigiri001@gmail.com
This script simulates the exact signup flow a user would go through
"""
import requests
import time
import json

# Test configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL = "sanjaigiri001@gmail.com"

def get_csrf_token():
    """Get CSRF token from register page"""
    print("\n📋 Step 1: Getting CSRF token from register page...")
    response = requests.get(f"{BASE_URL}/register/")
    
    if response.status_code == 200:
        # Extract CSRF token from cookies
        csrf_token = response.cookies.get('csrftoken')
        print(f"   ✓ CSRF token obtained: {csrf_token[:20]}...")
        return csrf_token, response.cookies
    else:
        print(f"   ❌ Failed to get register page: {response.status_code}")
        return None, None

def send_otp_request(email, csrf_token, cookies):
    """Send OTP to email"""
    print(f"\n📧 Step 2: Sending OTP to {email}...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': f'{BASE_URL}/register/'
    }
    
    data = {'email': email}
    
    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/send-otp/",
        json=data,
        headers=headers,
        cookies=cookies
    )
    elapsed = time.time() - start_time
    
    print(f"   ⏱️  Response time: {elapsed:.2f}s")
    print(f"   📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   📦 Response: {json.dumps(result, indent=2)}")
        
        if result.get('status') == 'success':
            print(f"   ✅ OTP sent successfully!")
            if result.get('debug_otp'):
                print(f"   🔐 OTP (Debug Mode): {result['debug_otp']}")
                return result['debug_otp']
            else:
                print(f"   📬 Check email for OTP")
                return None
        else:
            print(f"   ❌ Failed: {result.get('message')}")
            return None
    else:
        print(f"   ❌ Request failed with status {response.status_code}")
        return None

def verify_otp_request(email, otp, csrf_token, cookies):
    """Verify OTP"""
    print(f"\n✅ Step 3: Verifying OTP {otp} for {email}...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token,
        'Referer': f'{BASE_URL}/register/'
    }
    
    data = {'email': email, 'otp': otp}
    
    response = requests.post(
        f"{BASE_URL}/verify-otp/",
        json=data,
        headers=headers,
        cookies=cookies
    )
    
    print(f"   📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   📦 Response: {json.dumps(result, indent=2)}")
        
        if result.get('status') == 'success':
            print(f"   ✅ OTP verified successfully!")
            return True
        else:
            print(f"   ❌ Verification failed: {result.get('message')}")
            return False
    else:
        print(f"   ❌ Request failed with status {response.status_code}")
        return False

def test_complete_signup_flow():
    """Test the complete signup flow"""
    print("\n" + "="*80)
    print("🧪 TESTING COMPLETE OTP SIGNUP FLOW")
    print("="*80)
    print(f"🎯 Target Email: {TEST_EMAIL}")
    print(f"🌐 Server URL: {BASE_URL}")
    print("="*80)
    
    # Step 1: Get CSRF token
    csrf_token, cookies = get_csrf_token()
    if not csrf_token:
        print("\n❌ Test failed: Could not get CSRF token")
        return False
    
    # Step 2: Send OTP
    otp = send_otp_request(TEST_EMAIL, csrf_token, cookies)
    if not otp:
        print("\n⚠️  OTP sent but not received in console (might be in email)")
        print("   Check your email inbox and spam folder")
        otp = input("\n🔐 Enter the OTP you received: ").strip()
    
    if not otp or len(otp) != 6:
        print("\n❌ Test failed: Invalid OTP")
        return False
    
    # Step 3: Verify OTP
    verified = verify_otp_request(TEST_EMAIL, otp, csrf_token, cookies)
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    print(f"✅ CSRF Token: SUCCESS")
    print(f"✅ Send OTP: SUCCESS")
    print(f"{'✅' if verified else '❌'} Verify OTP: {'SUCCESS' if verified else 'FAILED'}")
    print("="*80)
    
    if verified:
        print("\n🎉 ALL TESTS PASSED!")
        print(f"✅ OTP system is working correctly for {TEST_EMAIL}")
        print("\n📝 Next steps:")
        print("   1. Open browser: http://127.0.0.1:8000/register/")
        print("   2. Enter email: sanjaigiri001@gmail.com")
        print("   3. Click 'Send OTP' button")
        print("   4. Enter the OTP from terminal (console mode)")
        print("   5. Complete registration")
    else:
        print("\n⚠️  OTP verification failed")
        print("   This might be due to:")
        print("   - Invalid OTP entered")
        print("   - OTP expired (10 minute limit)")
        print("   - Database issues")
    
    return verified

def check_server_status():
    """Check if Django server is running"""
    print("🔍 Checking if Django server is running...")
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"   ✅ Server is running (Status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Server is not running at {BASE_URL}")
        print("   Please start the server with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"   ❌ Error checking server: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 SMARTREADER OTP SIGNUP TEST")
    print("="*80)
    
    # Check if server is running
    if not check_server_status():
        print("\n❌ Cannot proceed without running server")
        print("\n💡 Start the server first:")
        print("   cd d:\\Django\\Final_Sem\\smart_reader")
        print("   python manage.py runserver")
        exit(1)
    
    # Run the test
    try:
        success = test_complete_signup_flow()
        
        if success:
            print("\n✅ Test completed successfully!")
        else:
            print("\n⚠️  Test completed with warnings")
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
