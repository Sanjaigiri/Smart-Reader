"""
MANUAL OTP TEST GUIDE
=====================
Follow these steps to test the OTP functionality
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║          🧪 MANUAL OTP TESTING GUIDE                         ║
╔══════════════════════════════════════════════════════════════╗

📋 CURRENT CONFIGURATION:
   • Email: harishoffil5@gmail.com
   • Mode: CONSOLE (OTP printed in terminal)
   • Real Email: Disabled (for testing)

═══════════════════════════════════════════════════════════════

🎯 TEST STEPS:

1. OPEN SIGNUP PAGE
   ✓ Already opened in browser: http://127.0.0.1:8000/register/

2. ENTER TEST EMAIL
   • Use: harishoffil5@gmail.com
   • Or any other email address

3. CLICK "SEND OTP"
   • Watch the Django terminal/console
   • OTP will be printed there like:
   
   ============================================================
   📧 OTP GENERATED
      Email: harishoffil5@gmail.com
      OTP: 123456  ← THIS IS YOUR OTP CODE
      Expires at: 2026-02-10 13:20:00
   ============================================================

4. COPY THE OTP
   • Copy the 6-digit code from terminal

5. ENTER OTP IN FORM
   • Paste the OTP in the verification field
   • Complete signup with:
     - Name: Your Name
     - Password: (at least 8 characters)

6. CLICK REGISTER
   • If OTP is correct and not expired → Success! ✓
   • If OTP is wrong → Error message

═══════════════════════════════════════════════════════════════

✅ EXPECTED RESULTS (Console Mode):

✓ Click "Send OTP" → Success message appears
✓ Django terminal → OTP code printed (6 digits)
✓ Enter OTP → Verification successful
✓ Complete form → Registration successful
✓ Redirected to login page

═══════════════════════════════════════════════════════════════

🔥 TO ENABLE REAL EMAIL SENDING:

1. GET GMAIL APP PASSWORD
   Go to: https://myaccount.google.com/apppasswords
   
   ⚠️ IMPORTANT: 
   - You NEED 2-Step Verification enabled first
   - Your regular Gmail password "sanjai giri 123" will NOT work
   - You need a 16-character App Password from Google

2. STEPS TO GET APP PASSWORD:
   a) Visit: https://myaccount.google.com/apppasswords
   b) Sign in with: harishoffil5@gmail.com
   c) If asked, enable 2-Step Verification first
   d) Select app: "Mail"
   e) Select device: "Other" → Type: SmartReader
   f) Click "Generate"
   g) Copy the 16-character code (example: abcd efgh ijkl mnop)
   h) Remove spaces: abcdefghijklmnop

3. UPDATE .ENV FILE
   Open: smart_reader/.env
   
   Change line:
   EMAIL_HOST_PASSWORD=GET_APP_PASSWORD_FROM_GOOGLE
   
   To:
   EMAIL_HOST_PASSWORD=abcdefghijklmnop  ← Your actual 16-char code
   
   And change:
   USE_REAL_EMAIL=False
   
   To:
   USE_REAL_EMAIL=True

4. RESTART SERVER
   Press CTRL+BREAK in Django terminal
   Run: python manage.py runserver

5. TEST AGAIN
   • OTP will now be sent to actual email address
   • Should arrive within 10 seconds ⚡

═══════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING:

Q: "Send OTP" button does nothing?
A: Check browser console (F12) for JavaScript errors

Q: OTP doesn't appear in terminal?
A: Make sure you're watching the Django server terminal (not this one)

Q: OTP expired?
A: OTPs expire in 10 minutes. Request a new one.

Q: Want to test with real email but don't have App Password?
A: Keep using Console Mode for now. Get App Password later.

═══════════════════════════════════════════════════════════════

📞 QUICK REFERENCE:

Signup Page: http://127.0.0.1:8000/register/
Configuration File: smart_reader/.env
Server Terminal: Shows OTP codes in console mode

═══════════════════════════════════════════════════════════════

🚀 READY TO TEST!

Now:
1. Go to the browser window with signup page
2. Enter email: harishoffil5@gmail.com
3. Click "Send OTP"
4. Watch Django terminal for OTP code
5. Enter OTP and complete signup

═══════════════════════════════════════════════════════════════
""")
