# 🚀 QUICK SETUP: Send Real OTP Emails

## Current Issue
❌ OTPs are NOT being sent to your email ID
❌ They only print in terminal (console mode)

## Solution: Setup Gmail App Password (5 minutes)

### Step 1: Enable 2-Step Verification
1. Go to: https://myaccount.google.com/security
2. Scroll to "Signing in to Google"
3. Click "2-Step Verification"
4. Follow the steps to enable it (if not already enabled)

### Step 2: Generate App Password
1. Go to: **https://myaccount.google.com/apppasswords**
2. You might need to sign in again
3. Under "Select app" → Choose **Mail**
4. Under "Select device" → Choose **Other (Custom name)**
5. Type: **Django SmartReader**
6. Click **GENERATE**
7. Google shows you a 16-character password like: `abcd efgh ijkl mnop`
8. **COPY THIS PASSWORD** (you can't see it again!)

### Step 3: Update Django Settings
1. Open: `smart_reader/settings.py`
2. Find line 167: `EMAIL_HOST_PASSWORD = 'YOUR_GMAIL_APP_PASSWORD_HERE'`
3. Replace with your password (remove spaces):
   ```python
   EMAIL_HOST_PASSWORD = 'abcdefghijklmnop'
   ```
4. Find line 159: `USE_REAL_EMAIL = False`
5. Change to:
   ```python
   USE_REAL_EMAIL = True
   ```

### Step 4: Restart Server
```powershell
# Stop server: Ctrl+C
# Start again:
python manage.py runserver
```

### Step 5: Test!
1. Go to: http://127.0.0.1:8000/register/
2. Enter your email ID
3. Click "Send OTP"
4. **Check your email inbox!** 📧
5. You should receive OTP within seconds

---

## Alternative: Use Console Mode (Testing)
If you don't want to setup Gmail yet:
- Keep `USE_REAL_EMAIL = False`
- When you click "Send OTP", look at your **terminal window**
- The OTP will be printed there like:
  ```
  ============================================================
  📧 OTP GENERATED
     Email: your@email.com
     OTP: 123456
  ============================================================
  ```
- Copy the 6-digit OTP from terminal and use it

---

## Troubleshooting

### "App passwords" option not showing?
→ Make sure 2-Step Verification is enabled first

### Email not receiving OTP?
1. Check spam/junk folder
2. Verify `EMAIL_HOST_USER` in settings.py matches your Gmail
3. Make sure you copied app password correctly (16 characters, no spaces)
4. Restart Django server after changing settings

### Still having issues?
→ Check terminal for error messages when clicking "Send OTP"

---

## Summary
✅ **Login eye icon** - Fixed with `!important` padding
✅ **Real email OTP** - Follow 3 steps above to setup Gmail App Password

**Current Status:** OTPs print in terminal (USE_REAL_EMAIL = False)
**To Fix:** Get Gmail App Password → Update settings.py → Restart server
