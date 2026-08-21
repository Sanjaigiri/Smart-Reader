# Email Setup Guide for OTP Functionality

## Problem Summary
The OTP (One-Time Password) emails are not being sent to users during registration because:
1. Email sending is currently disabled (using console backend)
2. Gmail App Password is not configured

## Solution

### Step 1: Get Gmail App Password

1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/

2. **Enable 2-Step Verification** (if not already enabled)
   - Go to Security → 2-Step Verification
   - Follow the prompts to enable it

3. **Generate App Password**
   - Visit: https://myaccount.google.com/apppasswords
   - OR go to: Security → 2-Step Verification → App passwords
   - Select app: **Mail**
   - Select device: **Other (Custom name)**
   - Enter name: **SmartReader Django App**
   - Click **Generate**
   - Google will show you a 16-character password (e.g., `abcd efgh ijkl mnop`)
   - **COPY THIS PASSWORD** - you won't be able to see it again!

### Step 2: Configure Django Settings

1. Open `smart_reader/settings.py`
2. Find the `EMAIL_HOST_PASSWORD` line (around line 161)
3. Replace `'YOUR_GMAIL_APP_PASSWORD_HERE'` with your 16-character app password
4. Remove spaces from the password when pasting

Example:
```python
EMAIL_HOST_PASSWORD = 'abcdefghijklmnop'  # Your actual 16-char app password (no spaces)
```

### Step 3: Verify Email Configuration

The settings have already been updated to use real email:
- `USE_REAL_EMAIL = True` (line 154)
- `EMAIL_HOST_USER = 'sanjaigiri001@gmail.com'`
- You just need to add the app password!

### Step 4: Test OTP Sending

1. Restart your Django development server
2. Go to the registration page
3. Enter an email address
4. Click "Send OTP"
5. Check the email inbox for the OTP

## Regarding the Eye Icon Issue

After reviewing the code in `reader/Templates/auth/register.html`:
- Each password field has **exactly ONE eye icon**
- Password field (line 319-321): One eye icon
- Confirm Password field (line 337-339): One eye icon

**If you're seeing two eye icons in one field:**
1. Clear your browser cache (Ctrl + Shift + Delete)
2. Hard reload the page (Ctrl + Shift + R)
3. Try a different browser
4. Check if any browser extensions might be interfering

The HTML structure is correct with proper positioning:
```html
<div class="input-group">
    <i class="fas fa-lock icon-left"></i>  <!-- Lock icon on left -->
    <input type="password" ... >
    <button type="button" class="password-toggle">  <!-- Eye icon on right -->
        <i class="fas fa-eye"></i>
    </button>
</div>
```

## Alternative: Use Console Backend for Development

If you don't want to set up Gmail:
1. In `settings.py`, change `USE_REAL_EMAIL = False`
2. OTPs will be printed in the terminal/console where Django is running
3. Copy the OTP from the terminal output and paste it in the registration form

## Troubleshooting

### Email Not Sending
- **Check Gmail App Password**: Make sure it's correct (16 characters, no spaces)
- **Check 2-Step Verification**: Must be enabled for app passwords to work
- **Check Firewall**: Port 587 must be open for SMTP
- **Check Error Logs**: Look at the Django terminal for error messages

### Still Not Working?
- Enable console backend temporarily: `USE_REAL_EMAIL = False`
- OTPs will print in the terminal
- This is useful for development/testing

## Security Notes
⚠️ **IMPORTANT**: 
- Never commit your Gmail App Password to Git
- Keep your `settings.py` secure
- Consider using environment variables for production:
  ```python
  import os
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
  ```

## Current Configuration Status
✅ Email settings configured to use Gmail SMTP
✅ From address set to: sanjaigiri001@gmail.com
⚠️ **ACTION NEEDED**: Add your Gmail App Password to `settings.py`

---
Last Updated: January 5, 2026
