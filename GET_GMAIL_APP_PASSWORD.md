# 🔐 GET YOUR GMAIL APP PASSWORD - 3 MINUTES

## ⚠️ IMPORTANT: You need to complete this to receive OTP in your email!

Your email: **sanjaigiri001@gmail.com**

---

## 📝 Step-by-Step Guide

### Step 1: Enable 2-Step Verification (If not already enabled)
1. Go to: https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Click and follow the setup process
4. ✅ This is required for App Passwords!

### Step 2: Generate App Password
1. **Visit:** https://myaccount.google.com/apppasswords
2. **Sign in** with your Gmail account: `sanjaigiri001@gmail.com`
3. **App name:** Type "SmartReader" or "Django OTP"
4. **Click:** "Create" button
5. **Copy** the 16-character password that appears

**Example of what you'll see:**
```
abcd efgh ijkl mnop
```

### Step 3: Remove Spaces
The password has spaces, but you need to remove them:
```
abcdefghijklmnop
```
Copy this version (no spaces, 16 characters)

### Step 4: Update .env File
1. Open: `d:\Django\Final_Sem\smart_reader\.env`
2. Find this line:
   ```
   EMAIL_HOST_PASSWORD=YOUR_APP_PASSWORD_HERE
   ```
3. Replace `YOUR_APP_PASSWORD_HERE` with your 16-character password (no spaces)
4. Save the file

**Example:**
```env
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

### Step 5: Restart Django Server
1. In terminal, press `Ctrl + C` to stop the server
2. Run again:
   ```bash
   cd d:\Django\Final_Sem\smart_reader
   python manage.py runserver
   ```

---

## ✅ Test It!

1. Open browser: http://127.0.0.1:8000/register/
2. Enter email: `sanjaigiri001@gmail.com`
3. Click "Send OTP"
4. **Check your email inbox!** 📧
5. OTP will arrive in **under 10 seconds**
6. Also check **spam folder** if not in inbox

---

## 🎯 Current Configuration

File: `d:\Django\Final_Sem\smart_reader\.env`

```env
USE_REAL_EMAIL=True                          ✅ ENABLED
EMAIL_HOST_USER=sanjaigiri001@gmail.com     ✅ YOUR EMAIL
EMAIL_HOST_PASSWORD=YOUR_APP_PASSWORD_HERE   ⚠️ NEED TO UPDATE
```

---

## 🔧 Troubleshooting

### "App Passwords option not available"
- **Solution:** Enable 2-Step Verification first
- Go to: https://myaccount.google.com/security

### "Invalid credentials" error
- **Check:** Did you remove all spaces from the password?
- **Check:** Did you copy the entire 16-character password?
- **Try:** Generate a new App Password

### Email not received
- **Check:** Spam folder
- **Check:** Gmail "All Mail" folder
- **Wait:** Up to 30 seconds (usually < 10 seconds)
- **Check:** Django terminal for any error messages

---

## 📧 What Happens Next

After you add the App Password:

1. ✅ OTP will be sent to your email
2. ✅ Professional email template
3. ✅ Delivery time: < 10 seconds
4. ✅ No more terminal/console mode

**Sample Email:**
```
Subject: 🔐 SmartReader - Email Verification OTP

Hello!

Your verification code for SmartReader is: 123456

[Large gradient box with OTP]

This code will expire in 10 minutes.
```

---

## 🚀 Quick Commands

```bash
# Navigate to project
cd d:\Django\Final_Sem\smart_reader

# Edit .env file (add your App Password)
notepad .env

# Restart server
python manage.py runserver

# Test in browser
http://127.0.0.1:8000/register/
```

---

## ✅ Checklist

- [ ] Enable 2-Step Verification on Gmail
- [ ] Generate App Password
- [ ] Remove spaces from password
- [ ] Update .env file with password
- [ ] Save .env file
- [ ] Restart Django server
- [ ] Test signup page
- [ ] Check email inbox

---

**🎯 Your Goal:** Replace `YOUR_APP_PASSWORD_HERE` in `.env` with your Gmail App Password

**⏱️ Time Required:** 3-5 minutes

**📧 Result:** OTP sent to sanjaigiri001@gmail.com instantly!
