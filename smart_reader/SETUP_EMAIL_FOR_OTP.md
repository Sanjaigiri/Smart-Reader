# 📧 SETUP REAL EMAIL FOR OTP SENDING

## Current Issue
- OTP emails are not being sent to users' email addresses
- `.env` file has `USE_REAL_EMAIL=False` (console mode)
- Need to enable real email sending using Gmail SMTP

## Quick Fix (5 Minutes)

### Step 1: Get Gmail App Password

1. **Visit:** https://myaccount.google.com/apppasswords
2. **Sign in** with your Gmail account (the one you want to send OTPs from)
3. **Important:** Make sure 2-Step Verification is enabled first!
   - If not enabled: https://myaccount.google.com/security
4. **Create App Password:**
   - App name: `SmartReader` (or any name)
   - Click "Create"
   - Copy the **16-character password** (example: `abcd efgh ijkl mnop`)
5. **Remove spaces** from the password: `abcdefghijklmnop`

### Step 2: Update .env File

Open the `.env` file in the `smart_reader` folder and update:

```env
USE_REAL_EMAIL=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_char_app_password_here
DEFAULT_FROM_EMAIL=SmartReader <your_email@gmail.com>
```

**Example:**
```env
USE_REAL_EMAIL=True
EMAIL_HOST_USER=sriakilkaviraj2005@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=SmartReader <sriakilkaviraj2005@gmail.com>
```

### Step 3: Restart Django Server

1. **Stop the current server** (press `CTRL+C` or `CTRL+BREAK` in terminal)
2. **Start it again:**
   ```bash
   cd D:\Django\Final_Sem\smart_reader
   python manage.py runserver
   ```

### Step 4: Test OTP Email

Run the test script:
```bash
cd D:\Django\Final_Sem\smart_reader
python test_otp_real_email.py
```

This will send a test email to verify everything works!

## ✅ Verification

After setup, when a user:
1. Goes to signup page
2. Enters email: `sriakilkaviraj2005@gmail.com`
3. Clicks "Send OTP"
4. **OTP will be sent to their email within 5-10 seconds!**
5. Check inbox (and spam/junk folder)

## 🔧 Troubleshooting

### "Authentication failed" error
- Make sure you're using **App Password**, not your regular Gmail password
- App Password must be 16 characters without spaces

### "2-Step Verification required" error
- Enable 2FA on your Google account first
- Visit: https://myaccount.google.com/security

### OTP not received after 60 seconds
- Check spam/junk folder
- Make sure `USE_REAL_EMAIL=True` in `.env`
- Verify email settings are correct
- Run the test script to diagnose

### Gmail App Password not working
1. Delete the old App Password
2. Generate a new one
3. Update `.env` file
4. Restart server

## 📝 Notes

- **Free Gmail accounts can send 500 emails/day**
- OTP emails are sent instantly (within 5-10 seconds)
- Each OTP expires in 10 minutes
- System automatically handles retries and errors
