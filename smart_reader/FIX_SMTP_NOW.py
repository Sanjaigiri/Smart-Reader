"""
Complete SMTP OTP Solution
===========================
This script will guide you through fixing the SMTP authentication issue.
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║                   🔴 SMTP AUTHENTICATION FAILED                  ║
╔══════════════════════════════════════════════════════════════════╗

📧 Email: harishoffil5@gmail.com
🔑 Password: sanjai giri 123

❌ ERROR: (535) Username and Password not accepted

══════════════════════════════════════════════════════════════════

🔍 WHY THIS HAPPENED:

Gmail does NOT accept your regular password for SMTP!

Your password "sanjai giri 123" works for:
   ✓ Logging into Gmail website
   ✓ Gmail mobile app
   ❌ SMTP (sending emails from apps) ← THIS IS WHAT WE NEED

For SMTP, you need a special "App Password" from Google.

══════════════════════════════════════════════════════════════════

✅ SOLUTION: GET GMAIL APP PASSWORD (5 minutes)

══════════════════════════════════════════════════════════════════

STEP 1: ENABLE 2-STEP VERIFICATION (if not already enabled)
──────────────────────────────────────────────────────────────────

1. Go to: https://myaccount.google.com/security

2. Find "2-Step Verification" section

3. Click "Get Started" or "Turn On"

4. Follow the steps:
   - Enter your phone number
   - Receive verification code via SMS
   - Confirm the code
   - Complete setup

5. ✓ 2-Step Verification is now enabled!

══════════════════════════════════════════════════════════════════

STEP 2: GENERATE APP PASSWORD
──────────────────────────────────────────────────────────────────

1. Go to: https://myaccount.google.com/apppasswords

2. Sign in with:
   Email: harishoffil5@gmail.com
   Password: sanjai giri 123

3. You'll see "App passwords" page

4. Under "Select app" → Choose: Mail

5. Under "Select device" → Choose: Other (Custom name)
   Type: SmartReader

6. Click "Generate" button

7. Google will show you a 16-character password like:
   
   ┌─────────────────────────────────────┐
   │  abcd efgh ijkl mnop                │
   │                                     │
   │  ⚠️  You won't see this again!      │
   └─────────────────────────────────────┘

8. IMPORTANT: Copy this password!
   Remove all spaces: abcdefghijklmnop

══════════════════════════════════════════════════════════════════

STEP 3: UPDATE YOUR .ENV FILE
──────────────────────────────────────────────────────────────────

1. Open file: smart_reader/.env

2. Find this line:
   EMAIL_HOST_PASSWORD=sanjai giri 123

3. Replace with your 16-character App Password:
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   
   ⚠️  NO SPACES in the password!

4. Make sure this line is set:
   USE_REAL_EMAIL=True

5. Save the file (Ctrl+S)

══════════════════════════════════════════════════════════════════

STEP 4: RESTART DJANGO SERVER
──────────────────────────────────────────────────────────────────

1. In the Django terminal, press: CTRL+BREAK

2. Wait for server to stop

3. Restart with:
   cd D:\\Django\\Final_Sem
   .venv\\Scripts\\Activate.ps1
   cd smart_reader
   python manage.py runserver

══════════════════════════════════════════════════════════════════

STEP 5: TEST OTP SENDING
──────────────────────────────────────────────────────────────────

1. Go to: http://127.0.0.1:8000/register/

2. Enter your email: harishoffil5@gmail.com

3. Click "Send OTP"

4. ✅ Check your Gmail inbox

5. OTP should arrive within 10 seconds! ⚡

══════════════════════════════════════════════════════════════════

📋 QUICK REFERENCE:

Get App Password: https://myaccount.google.com/apppasswords
Your Email: harishoffil5@gmail.com
Your Regular Password: sanjai giri 123 (for signing in to Google)
App Password: ________________ (16 chars - you'll get this)

File to Update: smart_reader/.env
Line to Change: EMAIL_HOST_PASSWORD=your-16-char-app-password

══════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

Q: Can't find "App passwords" option?
A: You need to enable 2-Step Verification first.

Q: "App passwords" link is disabled?
A: Make sure 2-Step Verification is turned ON.

Q: Forgot the App Password?
A: No problem! Generate a new one. Old one will stop working.

Q: Still getting errors after setting App Password?
A: Make sure:
   - No spaces in the password
   - USE_REAL_EMAIL=True
   - Server was restarted
   - .env file was saved

══════════════════════════════════════════════════════════════════

🎯 SUMMARY:

Problem: Gmail password doesn't work for SMTP
Solution: Get 16-character App Password from Google
Fix: Update EMAIL_HOST_PASSWORD in .env file
Result: OTP emails will be sent successfully! 📧✅

══════════════════════════════════════════════════════════════════

🚀 START NOW:

Step 1: Open browser → https://myaccount.google.com/apppasswords
Step 2: Generate App Password → Copy 16-char code
Step 3: Update .env → Save file
Step 4: Restart server → Test OTP

══════════════════════════════════════════════════════════════════
""")

# Ask if user has App Password ready
print("\n" + "="*70)
response = input("Do you have the 16-character App Password ready? (y/n): ").strip().lower()

if response == 'y':
    print("\n✓ Great! Let's update your .env file.")
    app_password = input("\nEnter your 16-character App Password (no spaces): ").strip().replace(' ', '')
    
    if len(app_password) == 16:
        print(f"\n✓ App Password received: {'*' * 16}")
        print("\n📝 To update .env file:")
        print(f"   1. Open: smart_reader/.env")
        print(f"   2. Find: EMAIL_HOST_PASSWORD=sanjai giri 123")
        print(f"   3. Replace with: EMAIL_HOST_PASSWORD={app_password}")
        print(f"   4. Save file")
        print(f"   5. Restart Django server")
        print(f"\n✅ Then test OTP at: http://127.0.0.1:8000/register/")
    else:
        print(f"\n⚠️  Warning: App Password should be 16 characters, you entered {len(app_password)}")
        print(f"   Please double-check and try again.")
else:
    print("\n📋 Follow the steps above to get your App Password.")
    print("   Then run this script again!")

print("\n" + "="*70 + "\n")
