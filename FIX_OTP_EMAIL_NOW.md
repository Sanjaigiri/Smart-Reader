# 🔧 FIX OTP EMAIL SENDING - STEP BY STEP

## Current Problem
❌ When you click "Send OTP" in signup page, it says "OTP sent" but you DON'T receive it in your email
✅ OTP is only printing in the terminal/console (not sent to real email)

## Why?
The system is in "development mode" - `USE_REAL_EMAIL = False` in settings.py
This means emails are sent to console only, not to real email addresses.

## Solution (5 minutes)

### STEP 1: Get Gmail App Password

1. **Open this link:** https://myaccount.google.com/apppasswords
   - Sign in with: **sanjaigiri001@gmail.com**

2. **Enable 2-Step Verification** (if not already on):
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification" → Follow steps to enable

3. **Generate App Password:**
   - Back to: https://myaccount.google.com/apppasswords
   - "Select app" → Choose **Mail**
   - "Select device" → Choose **Other (Custom name)**
   - Type: **Django SmartReader**
   - Click **GENERATE**

4. **Copy the password:**
   - Google shows: `abcd efgh ijkl mnop` (example)
   - Remove spaces → `abcdefghijklmnop`
   - **SAVE THIS** (you can't see it again!)

### STEP 2: Update Settings File

1. **Open:** `D:\Django\Final_Sem\smart_reader\smart_reader\settings.py`

2. **Find Line 167:**
   ```python
   EMAIL_HOST_PASSWORD = 'YOUR_GMAIL_APP_PASSWORD_HERE'
   ```

3. **Replace with your password:**
   ```python
   EMAIL_HOST_PASSWORD = 'abcdefghijklmnop'  # Your actual password (no spaces)
   ```

4. **Find Line 169:**
   ```python
   USE_REAL_EMAIL = False
   ```

5. **Change to:**
   ```python
   USE_REAL_EMAIL = True
   ```

6. **SAVE the file** (Ctrl+S)

### STEP 3: Restart Django Server

In your terminal:
1. **Stop server:** Press `Ctrl+C`
2. **Start again:**
   ```powershell
   cd smart_reader
   python manage.py runserver
   ```

### STEP 4: Test It!

1. Open: http://127.0.0.1:8000/register/
2. Enter your email (any valid email you can access)
3. Click "Send OTP"
4. **Check your email inbox!** 📧
5. You should receive the OTP within 5-10 seconds
6. Check spam folder if not in inbox
7. Enter the OTP and complete signup

---

## Alternative: Continue with Console Mode

**If you don't want to setup Gmail right now:**

1. Keep `USE_REAL_EMAIL = False` in settings.py
2. When you click "Send OTP", look at your **terminal window**
3. The OTP will be printed like this:

```
============================================================
📧 OTP GENERATED
   Email: yourtest@email.com
   OTP: 847392
   Expires at: 2026-01-05 11:15:00+00:00
============================================================
```

4. Copy the 6-digit number and paste it in the signup form
5. Complete registration

---

## Summary

### For Real Email Sending:
1. ✅ Get Gmail App Password from Google
2. ✅ Update Line 167 in settings.py with your password
3. ✅ Change Line 169 to `USE_REAL_EMAIL = True`
4. ✅ Restart server
5. ✅ Test signup - OTP will be sent to real email!

### Login Eye Icon:
✅ **FIXED!** - Refresh the login page, the eye icon is now inside the password box

---

**Need Help?**
- Can't find App Passwords option? → Enable 2-Step Verification first
- Still not receiving emails? → Check spam folder
- See error in terminal? → Share the error message
