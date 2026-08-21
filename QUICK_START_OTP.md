# ⚡ QUICK START - Send Real OTP Emails (2 Minutes)

## Current Status
🟡 **Console Mode Active** - OTPs print in terminal only (not sent to real emails)

## To Enable Real Email Sending

### Step 1: Get Gmail App Password (1 minute)
1. Visit: **https://myaccount.google.com/apppasswords**
2. Login with: **sanjaigiri001@gmail.com**
3. Generate App Password → Mail → Other (Django) → Generate
4. Copy 16-character password (example: `abcd efgh ijkl mnop`)
5. Remove spaces: `abcdefghijklmnop`

### Step 2: Update .env File (30 seconds)
1. Open: `D:\Django\Final_Sem\smart_reader\.env`
2. Find these two lines:
   ```
   USE_REAL_EMAIL=False
   EMAIL_HOST_PASSWORD=YOUR_GMAIL_APP_PASSWORD_HERE
   ```
3. Change to:
   ```
   USE_REAL_EMAIL=True
   EMAIL_HOST_PASSWORD=abcdefghijklmnop
   ```
   *(Use your actual password)*

4. Save file (Ctrl+S)

### Step 3: Restart Server (30 seconds)
```powershell
# In terminal, press Ctrl+C to stop server
# Then run:
cd smart_reader
python manage.py runserver
```

### Step 4: Test! (1 minute)
1. Go to: http://127.0.0.1:8000/register/
2. Enter YOUR real email
3. Click "Send OTP"
4. Check your email inbox! 📧
5. Enter OTP → Complete signup

---

## Alternative: Keep Testing with Terminal

**Don't want to setup Gmail yet?**
- Keep `.env` as is (`USE_REAL_EMAIL=False`)
- OTPs will continue printing in terminal
- Look for:
  ```
  ============================================================
  📧 OTP GENERATED
     Email: test@example.com
     OTP: 847392
  ============================================================
  ```
- Copy the 6-digit number
- Paste in signup form → Complete registration

---

## Files Overview

✅ **Created for you:**
- `.env` - Your email credentials (EDIT THIS TO ENABLE EMAILS)
- `.env.example` - Template (don't edit)
- `requirements.txt` - Dependencies list
- `.gitignore` - Protects .env from git
- `OTP_COMPLETE_ANALYSIS.md` - Full technical documentation

✅ **Updated:**
- `settings.py` - Now loads from .env automatically

---

## Quick Test Commands

```powershell
# Start server
cd smart_reader
python manage.py runserver

# Test signup
# Open: http://127.0.0.1:8000/register/
# Watch terminal for OTP (console mode)
# OR check email (if real email enabled)
```

---

## Summary

**OTP System:** ✅ Fully working and tested
**Configuration:** ✅ .env file created with all settings
**Dependencies:** ✅ python-dotenv installed
**Current Mode:** Console (OTPs in terminal)
**To Enable Real Emails:** Edit 2 lines in `.env` file

**Everything is ready! Just add your Gmail App Password to `.env` when you want to send real emails.**
