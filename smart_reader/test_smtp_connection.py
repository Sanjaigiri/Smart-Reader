"""
SMTP Connection Test for OTP Email
===================================
Tests Gmail SMTP connection with your credentials
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl

print("\n" + "="*70)
print("📧 TESTING SMTP CONNECTION FOR OTP")
print("="*70)

# Email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'harishoffil5@gmail.com'
EMAIL_PASSWORD = 'sanjai giri 123'  # Your regular password

print(f"\n📋 Configuration:")
print(f"   Host: {EMAIL_HOST}")
print(f"   Port: {EMAIL_PORT}")
print(f"   User: {EMAIL_USER}")
print(f"   Password: {'*' * len(EMAIL_PASSWORD)} ({len(EMAIL_PASSWORD)} chars)")

print("\n🔄 Testing SMTP connection...")

try:
    # Create SMTP connection
    print("   ⏳ Connecting to Gmail SMTP server...")
    server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
    
    print("   ✓ Connected to SMTP server")
    
    # Start TLS encryption
    print("   ⏳ Starting TLS encryption...")
    context = ssl.create_default_context()
    server.starttls(context=context)
    
    print("   ✓ TLS encryption enabled")
    
    # Login
    print("   ⏳ Attempting login...")
    server.login(EMAIL_USER, EMAIL_PASSWORD)
    
    print("   ✓ LOGIN SUCCESSFUL!")
    
    # Ask if user wants to send test OTP
    print("\n" + "="*70)
    print("✅ SMTP CONNECTION IS WORKING!")
    print("="*70)
    
    test_email = input("\n📧 Enter email to receive test OTP (or press Enter to skip): ").strip()
    
    if test_email:
        print(f"\n📨 Sending test OTP to: {test_email}")
        
        # Generate test OTP
        import random
        test_otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        print(f"   🔐 Generated OTP: {test_otp}")
        
        # Create email message
        message = MIMEMultipart("alternative")
        message["Subject"] = "SmartReader - Test OTP"
        message["From"] = f"SmartReader <{EMAIL_USER}>"
        message["To"] = test_email
        
        # Plain text version
        text = f"""Your test OTP is: {test_otp}

This is a test email from SmartReader.

If you received this, your email configuration is working perfectly!

- SmartReader Team"""
        
        # HTML version
        html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:20px;font-family:Arial,sans-serif;background:#f5f5f5">
<div style="max-width:500px;margin:0 auto;background:#fff;padding:30px;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.1)">
<h2 style="color:#6366f1;text-align:center;margin:0 0 20px">📚 SmartReader - Test OTP</h2>
<p style="color:#333;font-size:18px;font-weight:bold;margin:20px 0 10px">Your test OTP is:</p>
<div style="background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:#fff;font-size:42px;font-weight:bold;text-align:center;padding:25px;border-radius:10px;letter-spacing:10px;margin:20px 0">{test_otp}</div>
<p style="color:#666;margin:15px 0;font-size:14px">This is a test email. If you received this, your email configuration is <strong>working perfectly!</strong></p>
<p style="color:#999;font-size:12px;margin:20px 0 0;text-align:center">- SmartReader Team</p>
</div>
</body>
</html>"""
        
        # Attach both versions
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        print("   ⏳ Sending email...")
        server.sendmail(EMAIL_USER, test_email, message.as_string())
        
        print("   ✅ TEST EMAIL SENT SUCCESSFULLY!")
        print(f"\n   📬 Check inbox: {test_email}")
        print("   💡 Also check spam/junk folder if not in inbox")
        print(f"   🔐 Test OTP: {test_otp}")
    
    # Close connection
    server.quit()
    print("\n" + "="*70)
    print("✅ SMTP TEST COMPLETE - EVERYTHING WORKING!")
    print("="*70)
    print("\n🎉 Your Gmail SMTP is configured correctly!")
    print("   OTP emails will be sent successfully.")
    
except smtplib.SMTPAuthenticationError as e:
    print("\n" + "="*70)
    print("❌ AUTHENTICATION FAILED")
    print("="*70)
    print(f"\nError: {e}")
    print("\n🔴 Your regular Gmail password does NOT work for SMTP!")
    print("\n💡 SOLUTION: You need Gmail App Password")
    print("\n📝 Steps to fix:")
    print("   1. Visit: https://myaccount.google.com/apppasswords")
    print("   2. Sign in with: harishoffil5@gmail.com")
    print("   3. Enable 2-Step Verification (if not enabled)")
    print("   4. Generate App Password:")
    print("      - Select app: Mail")
    print("      - Select device: Other (SmartReader)")
    print("      - Click Generate")
    print("   5. Copy 16-character password (e.g., abcd efgh ijkl mnop)")
    print("   6. Remove spaces: abcdefghijklmnop")
    print("\n   7. Update .env file:")
    print("      EMAIL_HOST_PASSWORD=abcdefghijklmnop")
    print("\n   8. Restart Django server")
    print("\n" + "="*70)
    
except smtplib.SMTPException as e:
    print("\n" + "="*70)
    print("❌ SMTP ERROR")
    print("="*70)
    print(f"\nError: {e}")
    print("\n💡 Possible issues:")
    print("   - Network/firewall blocking SMTP")
    print("   - Gmail security settings")
    print("   - Incorrect email configuration")
    
except Exception as e:
    print("\n" + "="*70)
    print("❌ UNEXPECTED ERROR")
    print("="*70)
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

print("\n")
