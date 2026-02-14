"""
SENDGRID SETUP - NO 2-STEP VERIFICATION NEEDED!
================================================
Free forever, 100 emails/day, super easy setup (3 minutes)
"""

print("""
╔══════════════════════════════════════════════════════════════════╗
║        🚀 SENDGRID SETUP - EASY EMAIL WITHOUT GMAIL HASSLE       ║
╔══════════════════════════════════════════════════════════════════╗

✅ NO 2-Step Verification needed
✅ NO Complex password setup
✅ 100 emails/day FREE forever
✅ Works in 3 minutes

══════════════════════════════════════════════════════════════════

📝 STEP 1: CREATE FREE SENDGRID ACCOUNT (1 minute)
──────────────────────────────────────────────────────────────────

1. Go to: https://signup.sendgrid.com/

2. Fill in:
   - Email: harishoffil5@gmail.com
   - Password: (create new password)
   - First Name: Your name
   - Last Name: Your name
   - Company: SmartReader (or anything)

3. Click "Create Account"

4. ✓ Verify email (check your Gmail inbox)

5. ✓ Account created!

══════════════════════════════════════════════════════════════════

📝 STEP 2: GET API KEY (1 minute)
──────────────────────────────────────────────────────────────────

1. Login to: https://app.sendgrid.com/

2. Go to: Settings → API Keys
   Direct link: https://app.sendgrid.com/settings/api_keys

3. Click "Create API Key" button

4. API Key Name: SmartReader_OTP

5. Permissions: Full Access (or "Mail Send" only)

6. Click "Create & View"

7. COPY THE API KEY! (looks like: SG.xxxxxxxxxxxxxxxxxx)
   
   ⚠️  You can only see this ONCE!

8. Save it somewhere safe

══════════════════════════════════════════════════════════════════

📝 STEP 3: UPDATE .ENV FILE (30 seconds)
──────────────────────────────────────────────────────────────────

1. Open: smart_reader/.env

2. Find this line:
   EMAIL_HOST_PASSWORD=PASTE_YOUR_SENDGRID_API_KEY_HERE

3. Replace with your API key:
   EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxx

4. Make sure these are set:
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_HOST_USER=apikey
   USE_REAL_EMAIL=True

5. Save file (Ctrl+S)

══════════════════════════════════════════════════════════════════

📝 STEP 4: VERIFY SENDER (IMPORTANT!)
──────────────────────────────────────────────────────────────────

SendGrid requires you to verify your "From" email address:

1. Go to: https://app.sendgrid.com/settings/sender_auth/senders

2. Click "Create New Sender"

3. Fill in:
   - From Name: SmartReader
   - From Email: harishoffil5@gmail.com
   - Reply To: harishoffil5@gmail.com
   - Company: SmartReader
   - Address: Any address
   - City: Any city
   - Country: India

4. Click "Create"

5. Check Gmail inbox - verify the email

6. ✓ Sender verified!

══════════════════════════════════════════════════════════════════

📝 STEP 5: RESTART SERVER & TEST (30 seconds)
──────────────────────────────────────────────────────────────────

1. Stop Django server (CTRL+BREAK)

2. Restart:
   python manage.py runserver

3. Go to: http://127.0.0.1:8000/register/

4. Enter ANY email address

5. Click "Send OTP"

6. ✅ OTP will be sent to that email!

7. Check inbox (and spam folder)

8. OTP arrives in seconds! ⚡

══════════════════════════════════════════════════════════════════

📋 CONFIGURATION SUMMARY
──────────────────────────────────────────────────────────────────

Service: SendGrid
Host: smtp.sendgrid.net
Port: 587
Username: apikey (always "apikey")
Password: Your SendGrid API Key (SG.xxx...)
From: harishoffil5@gmail.com (must be verified)

══════════════════════════════════════════════════════════════════

✅ ADVANTAGES OF SENDGRID:

✓ No 2-Step Verification needed
✓ No App Password hassle
✓ 100 emails/day FREE forever
✓ Fast delivery (< 5 seconds)
✓ Professional email service
✓ Works with ANY email address
✓ Better deliverability than Gmail
✓ Email analytics dashboard

══════════════════════════════════════════════════════════════════

⚡ ALTERNATIVE: BREVO (FORMERLY SENDINBLUE)
──────────────────────────────────────────────────────────────────

If SendGrid doesn't work, try Brevo:

1. Signup: https://www.brevo.com/
2. 300 emails/day FREE
3. Get SMTP credentials
4. Update .env:
   EMAIL_HOST=smtp-relay.brevo.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-brevo-email
   EMAIL_HOST_PASSWORD=your-brevo-smtp-key

══════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING
──────────────────────────────────────────────────────────────────

Q: OTP not received?
A: 1. Check spam folder
   2. Verify sender email in SendGrid
   3. Check SendGrid activity dashboard

Q: "Sender not verified" error?
A: Verify your "From" email in SendGrid settings

Q: API key not working?
A: Generate new API key, make sure "Mail Send" permission enabled

Q: Still prefer Gmail?
A: You MUST use App Password - no way around it

══════════════════════════════════════════════════════════════════

🎯 QUICK START:

1. Signup: https://signup.sendgrid.com/
2. Get API Key: https://app.sendgrid.com/settings/api_keys
3. Verify sender: https://app.sendgrid.com/settings/sender_auth
4. Update .env with API key
5. Restart server & test!

══════════════════════════════════════════════════════════════════

🚀 TOTAL TIME: 3 MINUTES
📧 RESULT: OTP sent to ANY email without Gmail restrictions!

══════════════════════════════════════════════════════════════════
""")

# Interactive helper
print("\n" + "="*70)
response = input("Do you want to use SendGrid (recommended)? (y/n): ").strip().lower()

if response == 'y':
    print("\n✅ Great choice! Follow these steps:")
    print("\n1. Open browser: https://signup.sendgrid.com/")
    print("2. Create account (1 min)")
    print("3. Get API Key: https://app.sendgrid.com/settings/api_keys")
    print("4. Verify sender: https://app.sendgrid.com/settings/sender_auth")
    print("5. Paste API Key in .env file")
    print("6. Restart server & test!")
    
    has_key = input("\nDo you already have SendGrid API Key? (y/n): ").strip().lower()
    if has_key == 'y':
        api_key = input("\nPaste your SendGrid API Key: ").strip()
        if api_key.startswith('SG.'):
            print(f"\n✅ API Key looks good!")
            print(f"\nUpdate .env file:")
            print(f"   EMAIL_HOST_PASSWORD={api_key}")
            print(f"\nThen restart server!")
        else:
            print("\n⚠️  API Key should start with 'SG.'")
            print("   Make sure you copied the full key")
else:
    print("\n💡 Alternatives:")
    print("   1. SendGrid - Easiest, no 2-step")
    print("   2. Brevo - 300 emails/day free")
    print("   3. Gmail - Requires App Password (2-step needed)")

print("\n" + "="*70 + "\n")
