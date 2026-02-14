#!/usr/bin/env python
"""
Quick Email Configuration Fixer for SmartReader
================================================
This script helps you set up Gmail App Password for OTP emails.

Usage:
    python fix_email_config.py
"""

import os
import re
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("📧 SmartReader Email Configuration Fixer")
    print("="*70)
    print("\n🎯 This will help you configure Gmail for sending OTP emails.\n")
    
    # Find .env file
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("❌ Error: .env file not found!")
        print(f"   Expected location: {env_path}")
        return
    
    print(f"✓ Found .env file: {env_path}\n")
    
    # Check current configuration
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_email = re.search(r'EMAIL_HOST_USER=(.+)', content)
    current_password = re.search(r'EMAIL_HOST_PASSWORD=(.+)', content)
    use_real_email = re.search(r'USE_REAL_EMAIL=(.+)', content)
    
    print("📋 Current Configuration:")
    print("   USE_REAL_EMAIL:", use_real_email.group(1) if use_real_email else "Not set")
    print("   EMAIL_HOST_USER:", current_email.group(1) if current_email else "Not set")
    
    if current_password:
        pwd = current_password.group(1).strip()
        if pwd == 'YOUR_APP_PASSWORD_HERE' or not pwd:
            print("   EMAIL_HOST_PASSWORD: ❌ NOT CONFIGURED")
        else:
            print(f"   EMAIL_HOST_PASSWORD: ✓ Set ({len(pwd)} characters)")
    
    print("\n" + "="*70)
    print("📝 INSTRUCTIONS TO GET GMAIL APP PASSWORD")
    print("="*70)
    print("""
1. Visit: https://myaccount.google.com/apppasswords
2. Sign in with your Gmail account
3. You might need to enable 2-Step Verification first
4. Under "Select app", choose "Mail"
5. Under "Select device", choose "Other (Custom name)"
6. Enter name: SmartReader
7. Click "Generate"
8. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)
9. IMPORTANT: Remove all spaces from the password

Example:
   Generated: abcd efgh ijkl mnop
   Use this:  abcdefghijklmnop  (no spaces)
    """)
    
    print("="*70)
    print("\n🔧 Let's configure your email settings:\n")
    
    # Get user input
    print(f"Current Gmail: {current_email.group(1) if current_email else 'Not set'}")
    email = input("Enter your Gmail address (or press Enter to keep current): ").strip()
    
    if not email and current_email:
        email = current_email.group(1)
    elif not email:
        print("❌ Email is required!")
        return
    
    # Validate email
    if not email.endswith('@gmail.com'):
        print("⚠️  Warning: Email should be a Gmail address (@gmail.com)")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    print(f"\n✓ Email: {email}")
    print("\nNow enter the 16-character App Password (no spaces):")
    print("Example: abcdefghijklmnop")
    
    password = input("Gmail App Password: ").strip().replace(' ', '')
    
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    if len(password) != 16:
        print(f"⚠️  Warning: App Password is usually 16 characters, you entered {len(password)}")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return
    
    # Update .env file
    print("\n🔄 Updating .env file...")
    
    # Replace or add settings
    new_content = content
    
    # Update USE_REAL_EMAIL
    if 'USE_REAL_EMAIL=' in new_content:
        new_content = re.sub(r'USE_REAL_EMAIL=.*', 'USE_REAL_EMAIL=True', new_content)
    else:
        new_content += '\nUSE_REAL_EMAIL=True\n'
    
    # Update EMAIL_HOST_USER
    if 'EMAIL_HOST_USER=' in new_content:
        new_content = re.sub(r'EMAIL_HOST_USER=.*', f'EMAIL_HOST_USER={email}', new_content)
    else:
        new_content += f'EMAIL_HOST_USER={email}\n'
    
    # Update EMAIL_HOST_PASSWORD
    if 'EMAIL_HOST_PASSWORD=' in new_content:
        new_content = re.sub(r'EMAIL_HOST_PASSWORD=.*', f'EMAIL_HOST_PASSWORD={password}', new_content)
    else:
        new_content += f'EMAIL_HOST_PASSWORD={password}\n'
    
    # Update DEFAULT_FROM_EMAIL
    if 'DEFAULT_FROM_EMAIL=' in new_content:
        new_content = re.sub(
            r'DEFAULT_FROM_EMAIL=.*', 
            f'DEFAULT_FROM_EMAIL=SmartReader <{email}>', 
            new_content
        )
    else:
        new_content += f'DEFAULT_FROM_EMAIL=SmartReader <{email}>\n'
    
    # Backup original file
    backup_path = env_path.with_suffix('.env.backup')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"   ✓ Backup created: {backup_path}")
    
    # Write new configuration
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"   ✓ Updated: {env_path}")
    
    print("\n" + "="*70)
    print("✅ EMAIL CONFIGURATION COMPLETE!")
    print("="*70)
    print(f"""
Configuration Summary:
   USE_REAL_EMAIL: True
   EMAIL_HOST_USER: {email}
   EMAIL_HOST_PASSWORD: {'*' * len(password)} ({len(password)} chars)
   DEFAULT_FROM_EMAIL: SmartReader <{email}>

Next Steps:
   1. Restart Django server (Ctrl+C then run again)
   2. Go to: http://127.0.0.1:8000/register/
   3. Test signup with a real email address
   4. OTP should arrive within 10 seconds! ⚡

If OTP still doesn't work:
   - Check if 2-Step Verification is enabled
   - Make sure you used App Password (not regular password)
   - Check spam/junk folder
   - Try generating a new App Password
    """)
    
    print("="*70)
    
    # Ask if user wants to test
    test = input("\n🧪 Would you like to test the email configuration now? (y/n): ").strip().lower()
    
    if test == 'y':
        print("\n🔄 Testing email configuration...\n")
        test_email(email, password)

def test_email(email, password):
    """Test email configuration by sending a test email"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        import django
        import os
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
        django.setup()
        
        # Override settings
        settings.USE_REAL_EMAIL = True
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        settings.EMAIL_HOST = 'smtp.gmail.com'
        settings.EMAIL_PORT = 587
        settings.EMAIL_USE_TLS = True
        settings.EMAIL_HOST_USER = email
        settings.EMAIL_HOST_PASSWORD = password
        settings.DEFAULT_FROM_EMAIL = f'SmartReader <{email}>'
        
        # Send test email
        test_otp = '123456'
        test_to_email = input("Enter email address to receive test OTP: ").strip()
        
        if not test_to_email:
            test_to_email = email  # Send to self
        
        print(f"\n📧 Sending test OTP to {test_to_email}...")
        
        send_mail(
            'SmartReader - Test OTP',
            f'Test OTP: {test_otp}\n\nIf you received this, your email configuration is working!',
            settings.DEFAULT_FROM_EMAIL,
            [test_to_email],
            fail_silently=False,
        )
        
        print("\n✅ Test email sent successfully!")
        print(f"   Check inbox: {test_to_email}")
        print("   (Also check spam folder)")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        print("\nCommon issues:")
        print("   - App Password is incorrect")
        print("   - 2-Step Verification not enabled")
        print("   - Less secure app access blocked")
        print("   - Network/firewall issues")
        print("\n💡 Try generating a new App Password at:")
        print("   https://myaccount.google.com/apppasswords")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuration cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
