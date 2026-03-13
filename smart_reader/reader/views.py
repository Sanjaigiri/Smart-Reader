import json
import re
import socket
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.core.paginator import Paginator
from django.utils import timezone, translation
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import timedelta, datetime
import io
from deep_translator import GoogleTranslator

from .models import (
    Article, ReadingProgress, Note, UserProfile, Category, Tag,
    Bookmark, Highlight, Rating, ReadingStreak, Achievement, 
    UserAchievement, ReadingList, ReadingListAccessAttempt, OTPVerification, SiteVisit, ArticleViewLog, Feedback
)

# Try to import reportlab for PDF generation
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ============ TRANSLATION HELPER ============
def translate_text(text, target_lang='en'):
    """
    Translate text to target language using deep-translator
    Returns original text if translation fails or target is 'en'
    """
    if not text or target_lang == 'en':
        return text
    
    try:
        # Split text into chunks if it's too long (Google Translator limit is ~5000 chars)
        max_length = 4500
        if len(text) <= max_length:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return translated
        else:
            # Split by paragraphs for better translation
            paragraphs = text.split('\n\n')
            translated_paragraphs = []
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) <= max_length:
                    current_chunk += para + "\n\n"
                else:
                    if current_chunk:
                        translated_paragraphs.append(
                            GoogleTranslator(source='auto', target=target_lang).translate(current_chunk.strip())
                        )
                    current_chunk = para + "\n\n"
            
            if current_chunk:
                translated_paragraphs.append(
                    GoogleTranslator(source='auto', target=target_lang).translate(current_chunk.strip())
                )
            
            return "\n\n".join(translated_paragraphs)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails


# ============ HOME ============
def home(request):
    # Get user's language preference
    user_language = 'EN'
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            user_language = profile.preferred_language if hasattr(profile, 'preferred_language') and profile.preferred_language else 'EN'
        except UserProfile.DoesNotExist:
            user_language = 'EN'
    
    featured_articles = Article.objects.filter(
        is_featured=True, 
        is_published=True,
        language=user_language
    )[:3]
    recent_articles = Article.objects.filter(
        is_published=True,
        language=user_language
    )[:6]
    
    # Show all categories on home page
    categories = Category.objects.all()
    
    # Stats for homepage - Display as 200,000+ for the homepage stat card
    total_articles = Article.objects.filter(is_published=True, language=user_language).count()
    display_articles = "200,000" if total_articles > 0 else "0"
    total_users = User.objects.count()
    total_reads = ReadingProgress.objects.filter(is_completed=True).count()
    
    context = {
        'featured_articles': featured_articles,
        'recent_articles': recent_articles,
        'categories': categories,
        'total_articles': display_articles,
        'total_users': total_users,
        'total_reads': total_reads,
    }
    return render(request, 'home.html', context)


# ============ AUTHENTICATION ============
# Admin emails that don't require OTP verification
ADMIN_EMAILS = ['sanjaigiri001@gmail.com', 'sanjaig111@gmail.com']

# Common email domain typos and their corrections
EMAIL_DOMAIN_TYPOS = {
    'gamil.com': 'gmail.com',
    'gmial.com': 'gmail.com',
    'gmal.com': 'gmail.com',
    'gmaill.com': 'gmail.com',
    'gnail.com': 'gmail.com',
    'gmali.com': 'gmail.com',
    'gmai.com': 'gmail.com',
    'gmail.con': 'gmail.com',
    'gmail.co': 'gmail.com',
    'gmail.cm': 'gmail.com',
    'gmaul.com': 'gmail.com',
    'gmil.com': 'gmail.com',
    'yaho.com': 'yahoo.com',
    'yahooo.com': 'yahoo.com',
    'yahoo.con': 'yahoo.com',
    'hotmal.com': 'hotmail.com',
    'hotmai.com': 'hotmail.com',
    'hotmail.con': 'hotmail.com',
    'outloo.com': 'outlook.com',
    'outlok.com': 'outlook.com',
    'outlook.con': 'outlook.com',
}

def check_email_typo(email):
    """Check if email domain has a common typo, return suggested correction or None"""
    if '@' not in email:
        return None
    domain = email.split('@')[1].lower()
    if domain in EMAIL_DOMAIN_TYPOS:
        username = email.split('@')[0]
        correct_domain = EMAIL_DOMAIN_TYPOS[domain]
        return f"{username}@{correct_domain}"
    return None

def validate_email_format(email):
    """Validate email format"""
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_otp_email(email, otp):
    """
    Send OTP to user's email - SIMPLE AND CLEAN
    Just the OTP, nothing else
    """
    import time
    start_time = time.time()
    
    print(f"\n{'='*70}")
    print(f"📧 SENDING OTP EMAIL")
    print(f"{'='*70}")
    print(f"   📨 To: {email}")
    print(f"   🔐 OTP: {otp}")
    
    subject = 'SmartReader - Your Verification Code'
    
    # Plain text fallback
    message = f'''SmartReader - Email Verification

Your OTP Code: {otp}

This code is valid for 10 minutes.
If you did not request this code, please ignore this email.

- SmartReader Team'''
    
    # Beautiful HTML email with logo and branding
    html_message = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#f4f4f5;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#f4f4f5;padding:40px 20px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:480px;background-color:#ffffff;border-radius:16px;box-shadow:0 4px 24px rgba(0,0,0,0.08);overflow:hidden;">
                    <!-- Header with gradient -->
                    <tr>
                        <td style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#a855f7 100%);padding:32px 24px;text-align:center;">
                            <!-- Logo Icon -->
                            <div style="background:#ffffff;width:64px;height:64px;border-radius:16px;margin:0 auto 16px;display:inline-block;line-height:64px;">
                                <span style="font-size:32px;">📚</span>
                            </div>
                            <h1 style="color:#ffffff;margin:0;font-size:28px;font-weight:700;letter-spacing:-0.5px;">SmartReader</h1>
                            <p style="color:rgba(255,255,255,0.9);margin:8px 0 0;font-size:14px;">Your Personal Reading Companion</p>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding:40px 32px;text-align:center;">
                            <h2 style="color:#1f2937;margin:0 0 8px;font-size:20px;font-weight:600;">Email Verification</h2>
                            <p style="color:#6b7280;margin:0 0 32px;font-size:15px;line-height:1.5;">Enter this code to verify your email address</p>
                            
                            <!-- OTP Code Box -->
                            <div style="background:linear-gradient(135deg,#f8fafc 0%,#f1f5f9 100%);border:2px solid #e2e8f0;border-radius:12px;padding:24px;margin:0 auto 32px;">
                                <div style="font-size:42px;font-weight:800;color:#1f2937;letter-spacing:12px;font-family:'Courier New',monospace;">{otp}</div>
                            </div>
                            
                            <!-- Timer -->
                            <div style="display:inline-block;background:#fef3c7;border-radius:20px;padding:8px 16px;">
                                <span style="color:#92400e;font-size:13px;font-weight:500;">⏱️ Valid for 10 minutes</span>
                            </div>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background:#f8fafc;padding:24px 32px;border-top:1px solid #e5e7eb;">
                            <p style="color:#9ca3af;margin:0;font-size:12px;line-height:1.6;text-align:center;">If you didn't request this code, you can safely ignore this email.<br>Someone may have entered your email by mistake.</p>
                        </td>
                    </tr>
                </table>
                <!-- Brand Footer -->
                <p style="color:#9ca3af;font-size:12px;margin:24px 0 0;text-align:center;">© 2026 SmartReader. All rights reserved.</p>
            </td>
        </tr>
    </table>
</body>
</html>'''
    
    try:
        from django.core.mail import EmailMultiAlternatives
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@smartreader.com'
        
        print(f"   ✓ Email Backend: {settings.EMAIL_BACKEND}")
        print(f"   ✓ USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
        print(f"   ✓ From: {from_email}")
        
        # Create email message with optimized settings and anti-spam headers
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[email],
            headers={
                'X-Priority': '1',  # High priority
                'X-MSMail-Priority': 'High',
                'Importance': 'high',
                'X-Mailer': 'SmartReader Email Service',
                'X-Auto-Response-Suppress': 'OOF, AutoReply',
                'List-Unsubscribe': '<mailto:unsubscribe@smartreader.com>',
                'Precedence': 'bulk',
                'Content-Type': 'text/html; charset=utf-8',
            }
        )
        email_msg.attach_alternative(html_message, "text/html")
        
        print(f"   🔄 Sending email with optimized SMTP...")
        
        # Use threading for faster response in console mode
        use_real_email = getattr(settings, 'USE_REAL_EMAIL', False)
        
        if use_real_email:
            # Real email - send with 20 second timeout protection
            import socket
            original_timeout = socket.getdefaulttimeout()
            socket.setdefaulttimeout(20)  # 20 second timeout for email delivery
            
            try:
                email_msg.send(fail_silently=False)
            finally:
                socket.setdefaulttimeout(original_timeout)
        else:
            # Console mode - immediate return
            email_msg.send(fail_silently=False)
        
        elapsed = time.time() - start_time
        print(f"\n   ✅ EMAIL SENT SUCCESSFULLY!")
        print(f"   ⚡ Delivery time: {elapsed:.2f}s")
        print(f"{'='*70}\n")
        return True
        
    except socket.timeout:
        elapsed = time.time() - start_time
        print(f"\n   ⚠️  SMTP Timeout after {elapsed:.2f}s")
        print(f"   💡 Email may still be delivered")
        print(f"{'='*70}\n")
        # Return True in debug mode so user can proceed
        return settings.DEBUG
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n   ❌ EMAIL ERROR after {elapsed:.2f}s")
        print(f"   Error: {str(e)}")
        
        # In debug mode, still allow OTP flow to work
        if settings.DEBUG:
            print(f"   ⚠️  [DEBUG MODE] OTP is still valid in database")
            print(f"   ✓ OTP {otp} saved for {email}")
            print(f"   💡 Check terminal output or fix email config")
            print(f"{'='*70}\n")
            return True
        
        print(f"{'='*70}\n")
        import traceback
        traceback.print_exc()
        return False


def send_otp(request):
    """Send OTP to email for verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            print(f"\n{'='*60}")
            print(f"🔍 DEBUG: send_otp() function called")
            print(f"   Email received: {email}")
            print(f"   DEBUG mode: {settings.DEBUG}")
            print(f"   USE_REAL_EMAIL: {settings.USE_REAL_EMAIL if hasattr(settings, 'USE_REAL_EMAIL') else 'Not set'}")
            print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
            print(f"{'='*60}\n")
            
            # Validate email format
            if not validate_email_format(email):
                print(f"❌ Email validation failed for: {email}")
                return JsonResponse({'status': 'error', 'message': 'Invalid email format'})
            
            # Check for common email domain typos
            suggested_email = check_email_typo(email)
            if suggested_email:
                print(f"⚠️ Email typo detected: {email} -> {suggested_email}")
                return JsonResponse({
                    'status': 'typo',
                    'message': f'Did you mean {suggested_email}? Please check your email address.',
                    'suggested_email': suggested_email
                })
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                print(f"❌ Email already registered: {email}")
                return JsonResponse({'status': 'error', 'message': 'Email already registered'})
            
            # Admin emails don't need OTP - auto verify
            if email in ADMIN_EMAILS:
                print(f"✓ Admin email detected: {email}")
                return JsonResponse({'status': 'admin', 'message': 'Admin email - OTP not required'})
            
            # Check rate limiting - max 5 OTPs per email per hour
            one_hour_ago = timezone.now() - timedelta(hours=1)
            recent_otps = OTPVerification.objects.filter(
                email=email,
                created_at__gte=one_hour_ago
            ).count()
            
            if recent_otps >= 5:
                print(f"❌ Rate limit exceeded for: {email}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Too many OTP requests. Please try again after 1 hour.'
                })
            
            # Generate secure OTP using secrets module
            otp = OTPVerification.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            print(f"✓ OTP generated: {otp}")
            
            # Delete old unverified OTPs for this email (cleanup)
            deleted_count = OTPVerification.objects.filter(
                email=email,
                is_verified=False
            ).delete()
            print(f"✓ Deleted {deleted_count[0]} old unverified OTP records")
            
            # Create new OTP record in database
            otp_record = OTPVerification.objects.create(
                email=email,
                otp=otp,
                expires_at=expires_at,
                is_verified=False,
                attempts=0
            )
            print(f"✓ OTP saved to database with ID: {otp_record.id}")
            
            # Print OTP to console (always visible in terminal)
            print(f"\n{'='*60}")
            print(f"📧 OTP GENERATED")
            print(f"   Email: {email}")
            print(f"   OTP: {otp}")
            print(f"   Expires at: {expires_at}")
            print(f"{'='*60}\n")
            
            # Send OTP email
            import time
            send_start = time.time()
            print(f"🔄 Attempting to send email...")
            
            email_sent = send_otp_email(email, otp)
            send_elapsed = time.time() - send_start
            
            print(f"📧 Email sent result: {email_sent} (took {send_elapsed:.2f} seconds)")
            
            if email_sent:
                message = f'✓ OTP sent to {email}!'
                
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'sent_time': f'{send_elapsed:.1f}s'
                })
            else:
                # This shouldn't happen in debug mode, but handle it anyway
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to send OTP. Please check email configuration.'
                })
                
        except Exception as e:
            print(f"\n❌ ERROR in send_otp: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f'Failed to send OTP: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def verify_otp(request):
    """Verify OTP entered by user"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            otp = data.get('otp', '').strip()
            
            print(f"\n[OTP VERIFY] Attempting to verify OTP '{otp}' for email '{email}'")
            
            if not email or not otp:
                return JsonResponse({'status': 'error', 'message': 'Email and OTP are required'})
            
            if len(otp) != 6:
                return JsonResponse({'status': 'error', 'message': 'OTP must be 6 digits'})
            
            try:
                otp_record = OTPVerification.objects.filter(
                    email=email,
                    otp=otp
                ).latest('created_at')
                
                # Check if expired
                if otp_record.is_expired():
                    print(f"[OTP VERIFY] OTP expired for {email}")
                    otp_record.delete()  # Clean up expired OTP
                    return JsonResponse({
                        'status': 'error',
                        'message': 'OTP has expired. Please request a new one.'
                    })
                
                # Check attempt limit (max 5 attempts)
                if otp_record.attempts >= 5:
                    print(f"[OTP VERIFY] Max attempts exceeded for {email}")
                    otp_record.delete()  # Delete after max attempts
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Maximum verification attempts exceeded. Please request a new OTP.'
                    })
                
                # Check if already verified
                if otp_record.is_verified:
                    print(f"[OTP VERIFY] OTP already verified for {email}")
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Email already verified'
                    })
                
                # Mark as verified
                otp_record.is_verified = True
                otp_record.save()
                
                print(f"[OTP VERIFY] ✓ OTP verified successfully for {email}")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Email verified successfully!'
                })
            
            except OTPVerification.DoesNotExist:
                print(f"[OTP VERIFY] Invalid OTP '{otp}' for {email}")
                
                # Try to increment attempts if OTP exists but doesn't match
                try:
                    latest_otp = OTPVerification.objects.filter(email=email).latest('created_at')
                    if not latest_otp.is_expired():
                        latest_otp.increment_attempts()
                        remaining = 5 - latest_otp.attempts
                        if remaining > 0:
                            return JsonResponse({
                                'status': 'error',
                                'message': f'Please enter the OTP correctly. {remaining} attempts left.'
                            })
                except OTPVerification.DoesNotExist:
                    pass
                
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please enter the OTP correctly.'
                })
                
        except Exception as e:
            print(f"[OTP VERIFY] Error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Error verifying OTP'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def send_password_reset_otp(request):
    """Send OTP for forgot password flow."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()

        if not validate_email_format(email):
            return JsonResponse({'status': 'error', 'message': 'Enter a valid email address.'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'No account found with this email.'}, status=404)

        if not user.is_active:
            return JsonResponse({'status': 'error', 'message': 'This account is deactivated. Contact support.'}, status=403)

        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_otps = OTPVerification.objects.filter(email=email, created_at__gte=one_hour_ago).count()
        if recent_otps >= 5:
            return JsonResponse({'status': 'error', 'message': 'Too many reset attempts. Please try again after 1 hour.'}, status=429)

        OTPVerification.objects.filter(email=email, is_verified=False).delete()

        otp = OTPVerification.generate_otp()
        OTPVerification.objects.create(
            email=email,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=10),
            is_verified=False,
            attempts=0
        )

        email_sent = send_otp_email(email, otp)
        if not email_sent:
            return JsonResponse({'status': 'error', 'message': 'Unable to send reset OTP right now.'}, status=500)

        return JsonResponse({'status': 'success', 'message': f'Reset OTP sent to {email}.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def reset_password_with_otp(request):
    """Reset password after verifying OTP."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        otp = data.get('otp', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        if not validate_email_format(email):
            return JsonResponse({'status': 'error', 'message': 'Enter a valid email address.'}, status=400)
        if len(otp) != 6 or not otp.isdigit():
            return JsonResponse({'status': 'error', 'message': 'Enter the 6-digit OTP sent to your email.'}, status=400)
        if len(new_password) < 8:
            return JsonResponse({'status': 'error', 'message': 'Password must be at least 8 characters.'}, status=400)
        if new_password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'}, status=400)

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'No account found with this email.'}, status=404)

        try:
            otp_record = OTPVerification.objects.filter(email=email, otp=otp).latest('created_at')
        except OTPVerification.DoesNotExist:
            latest_otp = OTPVerification.objects.filter(email=email).order_by('-created_at').first()
            if latest_otp and not latest_otp.is_expired():
                latest_otp.increment_attempts()
                if latest_otp.attempts >= 5:
                    latest_otp.delete()
                    return JsonResponse({'status': 'error', 'message': 'Too many wrong OTP attempts. Request a new OTP.'}, status=403)
            return JsonResponse({'status': 'error', 'message': 'Incorrect OTP.'}, status=400)

        if otp_record.is_expired():
            otp_record.delete()
            return JsonResponse({'status': 'error', 'message': 'OTP expired. Please request a new one.'}, status=400)

        if otp_record.attempts >= 5:
            otp_record.delete()
            return JsonResponse({'status': 'error', 'message': 'Too many wrong OTP attempts. Request a new OTP.'}, status=403)

        user.set_password(new_password)
        user.save()
        OTPVerification.objects.filter(email=email).delete()

        return JsonResponse({'status': 'success', 'message': 'Password reset successful. You can now sign in with your new password.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def check_email(request):
    """Check if email is valid and available"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        
        # Validate email format
        if not validate_email_format(email):
            return JsonResponse({'status': 'error', 'message': 'Invalid email format', 'valid': False})
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({'status': 'error', 'message': 'Email already registered', 'valid': False})
        
        return JsonResponse({'status': 'success', 'message': 'Email is available', 'valid': True})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        otp = request.POST.get('otp', '').strip()
        
        # Validate email format
        if not validate_email_format(email):
            messages.error(request, 'Please enter a valid email address!')
            return render(request, 'auth/register.html')
        
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'auth/register.html')
        
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters!')
            return render(request, 'auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'auth/register.html')
        
        # Skip OTP verification for admin emails
        is_admin_email = email in ADMIN_EMAILS
        
        if not is_admin_email:
            # Verify OTP for regular users - must be verified and not expired
            try:
                otp_record = OTPVerification.objects.filter(
                    email=email,
                    otp=otp,
                    is_verified=True
                ).latest('created_at')
                
                # Double-check expiration at registration time
                if otp_record.is_expired():
                    messages.error(request, 'OTP has expired. Please request a new one!')
                    otp_record.delete()
                    return render(request, 'auth/register.html')
                    
            except OTPVerification.DoesNotExist:
                messages.error(request, 'Please verify your email with OTP first!')
                return render(request, 'auth/register.html')
        
        # Generate username from email
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name
        )
        
        # Create profile and streak for new user
        UserProfile.objects.create(user=user, is_email_verified=True)
        ReadingStreak.objects.create(user=user)
        
        # Delete used OTP
        OTPVerification.objects.filter(email=email).delete()
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'auth/register.html')


def user_login(request):
    if request.user.is_authenticated:
        # Check if admin trying to access admin panel
        if request.user.email in ADMIN_EMAILS:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate by username or email
        user = authenticate(request, username=username, password=password)
        
        # If not found by username, try email
        if user is None:
            try:
                user_obj = User.objects.get(email=username.lower())
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None:
            # Check if user account is active
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Please contact support.')
                return render(request, 'auth/login.html')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username/email or password!')
    
    return render(request, 'auth/login.html')


def admin_login(request):
    """Separate admin login page"""
    if request.user.is_authenticated:
        if request.user.email in ADMIN_EMAILS or request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'You do not have admin privileges!')
            return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password')
        
        # Check if email is an admin email
        if email not in ADMIN_EMAILS:
            messages.error(request, 'This email is not authorized for admin access!')
            return render(request, 'auth/admin_login.html')
        
        # Try to authenticate
        try:
            user = User.objects.get(email=email)
            auth_user = authenticate(request, username=user.username, password=password)
            
            if auth_user is not None:
                # Check if admin account is active
                if not auth_user.is_active:
                    messages.error(request, 'Your admin account has been deactivated. Please contact the system administrator.')
                    return render(request, 'auth/admin_login.html')
                
                login(request, auth_user)
                messages.success(request, f'Welcome, Admin {auth_user.first_name or auth_user.username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid password!')
        except User.DoesNotExist:
            messages.error(request, 'Admin account not found. Please register first.')
    
    return render(request, 'auth/admin_login.html')


def user_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ============ ARTICLES ============
@login_required
def article_list(request):
    # Get user's preferred language for filtering
    user_profile = request.user.profile
    user_language = user_profile.preferred_language if hasattr(user_profile, 'preferred_language') else 'EN'
    
    # Filter articles by language and published status
    articles = Article.objects.filter(
        is_published=True,
        language=user_language
    )
    
    # Limit categories and tags shown - only top 8 categories and 15 tags
    categories_raw = Category.objects.annotate(article_count=Count('articles')).order_by('-article_count')[:8]
    
    # Add display counts (multiply by 10 to show as 10000+)
    categories = []
    for cat in categories_raw:
        cat.display_count = cat.article_count * 10 + 2000  # e.g., 1007 -> 12070
        categories.append(cat)
    
    tags = Tag.objects.annotate(article_count=Count('articles')).order_by('-article_count')[:15]
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query)
        )
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    
    # Filter by tag
    tag_slug = request.GET.get('tag')
    if tag_slug:
        articles = articles.filter(tags__slug=tag_slug)
    
    # Filter by difficulty
    difficulty = request.GET.get('difficulty')
    if difficulty:
        articles = articles.filter(difficulty=difficulty)
    
    # Sorting
    sort = request.GET.get('sort', '-created_at')
    if sort == 'popular':
        articles = articles.order_by('-views_count')
    elif sort == 'rating':
        articles = articles.annotate(avg_rating=Avg('ratings__score')).order_by('-avg_rating')
    else:
        articles = articles.order_by(sort)
    
    # Pagination
    paginator = Paginator(articles, 9)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    # Get user's bookmarks and progress
    user_bookmarks = []
    user_progress = {}
    if request.user.is_authenticated:
        user_bookmarks = list(Bookmark.objects.filter(user=request.user).values_list('article_id', flat=True))
        for prog in ReadingProgress.objects.filter(user=request.user):
            user_progress[prog.article_id] = prog.scroll_percentage
    
    context = {
        'articles': articles,
        'categories': categories,
        'tags': tags,
        'user_bookmarks': user_bookmarks,
        'user_progress': user_progress,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_difficulty': difficulty,
        'current_sort': sort,
        'search_query': query,
    }
    return render(request, 'articles/list.html', context)


@login_required
def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    
    # Increment view count
    article.views_count += 1
    article.save(update_fields=['views_count'])
    
    # User-specific data
    is_bookmarked = False
    user_rating = None
    user_notes = []
    user_notes_count = 0
    user_highlights = []
    progress = None
    user_language = 'EN'
    
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, article=article).exists()
        user_rating = Rating.objects.filter(user=request.user, article=article).first()
        user_notes_queryset = Note.objects.filter(user=request.user, article=article).order_by('-created_at')
        user_notes_count = user_notes_queryset.count()
        user_notes = user_notes_queryset[:3]
        user_highlights = Highlight.objects.filter(user=request.user, article=article)
        progress, _ = ReadingProgress.objects.get_or_create(
            user=request.user, article=article
        )
        
        # Update reading streak
        streak, _ = ReadingStreak.objects.get_or_create(user=request.user)
        if streak.last_read_date != timezone.now().date():
            streak.update_streak()
        
        # Get user's language preference
        try:
            profile = UserProfile.objects.get(user=request.user)
            user_language = profile.preferred_language if hasattr(profile, 'preferred_language') and profile.preferred_language else 'EN'
        except UserProfile.DoesNotExist:
            user_language = 'EN'
    
    # Get related articles (filter by language if available)
    related_articles = Article.objects.filter(
        category=article.category, 
        is_published=True,
        language=user_language
    ).exclude(id=article.id)[:4]
    
    # Get ratings
    avg_rating = article.ratings.aggregate(Avg('score'))['score__avg'] or 0
    rating_count = article.ratings.count()
    
    # Translation based on user language preference (optional feature - removed for now)
    translated_title = article.title
    translated_content = article.content
    translated_summary = article.summary
    
    context = {
        'article': article,
        'translated_title': translated_title,
        'translated_content': translated_content,
        'translated_summary': translated_summary,
        'user_language': user_language,
        'related_articles': related_articles,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'is_bookmarked': is_bookmarked,
        'user_rating': user_rating,
        'user_notes': user_notes,
        'user_notes_count': user_notes_count,
        'user_highlights': user_highlights,
        'progress': progress,
        'has_purchase_links': article.has_purchase_links(),
    }
    return render(request, 'articles/read.html', context)


@login_required
def read_article(request, id):
    """Legacy URL support"""
    article = get_object_or_404(Article, id=id)
    return redirect('article_detail', slug=article.slug)


# ============ READING PROGRESS ============
@csrf_exempt  # Allow sendBeacon requests without CSRF token header
@login_required
def save_progress(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        progress, created = ReadingProgress.objects.get_or_create(
            user=request.user,
            article_id=data['article_id']
        )
        
        new_percentage = data.get('percentage', 0)
        position = data.get('position', 0)
        time_delta = data.get('time', 0)
        
        # Update position
        progress.last_position = position
        progress.scroll_percentage = new_percentage
        
        # Only update max_scroll_percentage if new value is higher (progress only increases)
        if new_percentage > progress.max_scroll_percentage:
            progress.max_scroll_percentage = new_percentage
        
        # Add time spent
        progress.time_spent += time_delta
        
        # Check if article was just completed
        was_just_completed = False
        if not progress.is_completed and (progress.max_scroll_percentage >= 90 or new_percentage >= 100):
            progress.is_completed = True
            progress.max_scroll_percentage = 100  # Ensure 100% is stored when completed
            was_just_completed = True
        
        # Also ensure any already-completed article shows 100%
        if progress.is_completed and progress.max_scroll_percentage < 100:
            progress.max_scroll_percentage = 100
        
        progress.save()
        
        # Log article view
        ArticleViewLog.objects.create(
            article_id=data['article_id'],
            user=request.user,
            ip_address=get_client_ip(request),
            time_spent=time_delta
        )
        
        # Check for achievements
        check_achievements(request.user)
        
        # Calculate weekly progress for real-time feedback
        today = timezone.now().date()
        this_week_reads = ReadingProgress.objects.filter(
            user=request.user,
            is_completed=True,
            last_read_at__gte=today - timedelta(days=7)
        ).count()
        
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        weekly_goal_achieved = this_week_reads >= profile.reading_goal
        
        return JsonResponse({
            'status': 'saved', 
            'percentage': progress.scroll_percentage,
            'max_percentage': progress.max_scroll_percentage,
            'total_time': int(progress.time_spent),
            'just_completed': was_just_completed,
            'this_week_reads': this_week_reads,
            'reading_goal': profile.reading_goal,
            'weekly_goal_achieved': weekly_goal_achieved
        })
    
    return JsonResponse({'status': 'error'}, status=400)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ============ NOTES ============
@login_required
def save_note(request):
    if request.method == 'POST':
        article_id = request.POST.get('article_id')
        selected_text = request.POST.get('selected_text', '')
        note_text = request.POST.get('note', '')
        
        if note_text:
            Note.objects.create(
                user=request.user,
                article_id=article_id,
                selected_text=selected_text,
                note=note_text
            )
            messages.success(request, 'Note saved successfully!')
        
        article = get_object_or_404(Article, id=article_id)
        return redirect('article_detail', slug=article.slug)
    
    return redirect('articles')


@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    article_slug = note.article.slug
    note.delete()
    messages.success(request, 'Note deleted!')
    return redirect('article_detail', slug=article_slug)


@login_required
def my_notes(request):
    notes = Note.objects.filter(user=request.user).select_related('article')
    
    # Filter by article
    article_id = request.GET.get('article')
    if article_id:
        notes = notes.filter(article_id=article_id)
    
    # Search
    query = request.GET.get('q')
    if query:
        notes = notes.filter(
            Q(note__icontains=query) |
            Q(selected_text__icontains=query)
        )
    
    articles_with_notes = Article.objects.filter(
        notes__user=request.user
    ).distinct()
    
    context = {
        'notes': notes,
        'articles_with_notes': articles_with_notes,
    }
    return render(request, 'user/notes.html', context)


# ============ BOOKMARKS ============
@login_required
def toggle_bookmark(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            article_id = data.get('article_id')
            
            if not article_id:
                return JsonResponse({'status': 'error', 'message': 'Article ID required'}, status=400)
            
            # Ensure article_id is an integer
            try:
                article_id = int(article_id)
            except (ValueError, TypeError):
                return JsonResponse({'status': 'error', 'message': 'Invalid article ID'}, status=400)
            
            # Check if article exists
            try:
                article = Article.objects.get(id=article_id)
            except Article.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Article not found'}, status=404)
            
            bookmark, created = Bookmark.objects.get_or_create(
                user=request.user,
                article=article
            )
            
            if not created:
                bookmark.delete()
                return JsonResponse({'status': 'removed'})
            
            return JsonResponse({'status': 'added'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'POST method required'}, status=400)


@login_required
def my_bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('article')
    
    context = {
        'bookmarks': bookmarks,
    }
    return render(request, 'user/bookmarks.html', context)


# ============ HIGHLIGHTS ============
@login_required
def save_highlight(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        highlight = Highlight.objects.create(
            user=request.user,
            article_id=data['article_id'],
            text=data['text'],
            color=data.get('color', 'yellow'),
            start_offset=data.get('start_offset', 0),
            end_offset=data.get('end_offset', 0)
        )
        
        return JsonResponse({
            'status': 'saved',
            'highlight_id': highlight.id
        })
    
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def delete_highlight(request, highlight_id):
    if request.method == 'POST':
        highlight = get_object_or_404(Highlight, id=highlight_id, user=request.user)
        highlight.delete()
        return JsonResponse({'status': 'deleted'})
    
    return JsonResponse({'status': 'error'}, status=400)


# ============ RATINGS ============
@login_required
def rate_article(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        article_id = data.get('article_id')
        score = int(data.get('score', 0))
        review = data.get('review', '')
        
        if 1 <= score <= 5:
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                article_id=article_id,
                defaults={'score': score, 'review': review}
            )
            
            # Get updated average
            article = get_object_or_404(Article, id=article_id)
            avg_rating = article.ratings.aggregate(Avg('score'))['score__avg'] or 0
            
            return JsonResponse({
                'status': 'saved',
                'avg_rating': round(avg_rating, 1)
            })
    
    return JsonResponse({'status': 'error'}, status=400)


# ============ DASHBOARD ============
@login_required
def dashboard(request):
    user = request.user
    normalize_user_progress(user)
    
    # Reading Progress
    progress_list = ReadingProgress.objects.filter(user=user)
    completed_articles = progress_list.filter(is_completed=True).count()
    in_progress_articles = progress_list.filter(is_completed=False).count()
    total_time = progress_list.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
    
    # Convert to hours and minutes
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    
    # Reading Streak
    streak, _ = ReadingStreak.objects.get_or_create(user=user)
    
    # Recent Activity
    recent_progress = progress_list.order_by('-last_read_at')[:5]
    
    # Weekly Stats (for chart)
    today = timezone.now().date()
    week_stats = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        day_progress = progress_list.filter(last_read_at__date=day)
        week_stats.append({
            'day': day.strftime('%a'),
            'articles': day_progress.count(),
            'time': day_progress.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
        })
    
    # Achievements
    user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
    
    # Category Distribution
    category_stats = progress_list.values(
        'article__category__name'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    # Reading Goal Progress
    profile, _ = UserProfile.objects.get_or_create(user=user)
    this_week_reads = progress_list.filter(
        is_completed=True,
        last_read_at__gte=today - timedelta(days=7)
    ).count()
    goal_progress = min(100, (this_week_reads / profile.reading_goal) * 100) if profile.reading_goal > 0 else 0
    weekly_goal_achieved = this_week_reads >= profile.reading_goal
    
    # Check if we should show congratulations popup (only once per session)
    show_congrats = False
    if weekly_goal_achieved:
        session_key = f'goal_achieved_{today.isocalendar()[1]}_{user.id}'  # Week number + user id
        if not request.session.get(session_key, False):
            show_congrats = True
            request.session[session_key] = True
    
    # Get recently completed articles (last 5 completed this week)
    recent_completions = progress_list.filter(
        is_completed=True,
        last_read_at__gte=today - timedelta(days=7)
    ).select_related('article').order_by('-last_read_at')[:5]
    
    context = {
        'completed_articles': completed_articles,
        'in_progress_articles': in_progress_articles,
        'total_hours': hours,
        'total_minutes': minutes,
        'streak': streak,
        'recent_progress': recent_progress,
        'week_stats': json.dumps(week_stats),
        'user_achievements': user_achievements,
        'category_stats': category_stats,
        'goal_progress': goal_progress,
        'reading_goal': profile.reading_goal,
        'this_week_reads': this_week_reads,
        'weekly_goal_achieved': weekly_goal_achieved,
        'show_congrats': show_congrats,
        'recent_completions': recent_completions,
    }
    return render(request, 'user/dashboard.html', context)


# ============ PROFILE ============
@login_required
def profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update profile
        profile.bio = request.POST.get('bio', '')
        profile.reading_goal = int(request.POST.get('reading_goal', 5))
        
        # Handle dark mode - update theme field
        dark_mode_checked = request.POST.get('dark_mode') == 'on'
        profile.dark_mode = dark_mode_checked
        profile.theme = 'dark' if dark_mode_checked else 'light'
        
        # Handle language preference - store in database
        language = request.POST.get('language', 'EN').upper()
        profile.preferred_language = language
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            # Delete old avatar if it exists and is not the default
            if profile.avatar and 'default' not in profile.avatar.name:
                try:
                    profile.avatar.delete(save=False)
                except:
                    pass
            profile.avatar = avatar_file
        
        profile.save()
        
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    from reader.models import LANGUAGE_CHOICES
    
    # Get user statistics for profile display
    from reader.models import ReadingProgress, Note, Bookmark, ReadingStreak
    from datetime import timedelta
    total_articles = ReadingProgress.objects.filter(user=request.user, is_completed=True).count()
    total_notes = Note.objects.filter(user=request.user).count()
    bookmarks_count = Bookmark.objects.filter(user=request.user).count()
    
    # Get weekly articles read
    week_start = timezone.now() - timedelta(days=7)
    weekly_articles_read = ReadingProgress.objects.filter(
        user=request.user, 
        is_completed=True,
        last_read_at__gte=week_start
    ).count()
    
    # Get current reading streak
    try:
        streak = ReadingStreak.objects.get(user=request.user)
        reading_streak = streak.current_streak
    except ReadingStreak.DoesNotExist:
        reading_streak = 0
    
    context = {
        'profile': profile,
        'language_choices': LANGUAGE_CHOICES,
        'total_articles': total_articles,
        'total_notes': total_notes,
        'bookmarks_count': bookmarks_count,
        'reading_streak': reading_streak,
        'weekly_articles_read': weekly_articles_read,
    }
    return render(request, 'user/profile.html', context)


# ============ READING LISTS ============
@login_required
def reading_lists(request):
    lists = ReadingList.objects.filter(user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        pin = request.POST.get('private_pin', request.POST.get('access_pin', '')).strip()
        
        if name:
            if not is_public:
                is_valid_pin, pin_message = validate_reading_list_pin(pin)
                if not is_valid_pin:
                    messages.error(request, pin_message)
                    return redirect('reading_lists')

            reading_list = ReadingList(
                user=request.user,
                name=name,
                description=description,
                is_public=is_public
            )
            if is_public:
                reading_list.access_pin = ''
            else:
                reading_list.set_pin(pin)
            reading_list.save()
            messages.success(request, 'Reading list created!')
            return redirect('reading_lists')
    
    context = {
        'reading_lists': lists,
    }
    return render(request, 'user/reading_lists.html', context)


@login_required
def add_to_list(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        list_id = data.get('list_id')
        article_id = data.get('article_id')
        
        reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
        article = get_object_or_404(Article, id=article_id)
        
        reading_list.articles.add(article)
        
        return JsonResponse({'status': 'added'})
    
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def access_reading_list(request, list_id):
    """Unlock or fetch reading list contents."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
    articles = reading_list.articles.all().order_by('-created_at')

    if reading_list.is_public:
        return JsonResponse({
            'status': 'success',
            'description': reading_list.description or '',
            'articles': [
                {
                    'title': article.title,
                    'slug': article.slug,
                    'category': article.category.name if article.category else 'Uncategorized',
                    'read_time': article.estimated_read_time,
                }
                for article in articles
            ]
        })

    attempt, _ = ReadingListAccessAttempt.objects.get_or_create(
        user=request.user,
        reading_list=reading_list
    )

    if attempt.is_locked():
        return JsonResponse({
            'status': 'locked',
            'message': 'This private list is locked. Please try again after 24 hours.'
        }, status=403)

    pin = json.loads(request.body).get('pin', '').strip()
    is_valid_pin, pin_message = validate_reading_list_pin(pin)
    if not is_valid_pin:
        return JsonResponse({'status': 'error', 'message': pin_message}, status=400)

    if not reading_list.check_pin(pin):
        attempt.register_failure()
        if attempt.is_locked():
            return JsonResponse({
                'status': 'locked',
                'message': 'Wrong PIN entered 3 times. Please try again after 24 hours.'
            }, status=403)

        remaining_attempts = max(0, 3 - attempt.failed_attempts)
        return JsonResponse({
            'status': 'error',
            'message': f'Incorrect PIN. {remaining_attempts} attempt(s) left.'
        }, status=403)

    attempt.register_success()
    return JsonResponse({
        'status': 'success',
        'description': reading_list.description or '',
        'articles': [
            {
                'title': article.title,
                'slug': article.slug,
                'category': article.category.name if article.category else 'Uncategorized',
                'read_time': article.estimated_read_time,
            }
            for article in articles
        ]
    })


# ============ SEARCH ============
def search(request):
    query = request.GET.get('q', '')
    results = []
    
    # Get user's language preference
    user_language = 'EN'
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            user_language = profile.preferred_language if hasattr(profile, 'preferred_language') and profile.preferred_language else 'EN'
        except UserProfile.DoesNotExist:
            user_language = 'EN'
    
    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__name__icontains=query),
            is_published=True,
            language=user_language
        ).distinct()[:20]
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'search.html', context)


def search_suggestions(request):
    """API endpoint for search autocomplete"""
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    # Get user's language preference
    user_language = 'EN'
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            user_language = profile.preferred_language if hasattr(profile, 'preferred_language') and profile.preferred_language else 'EN'
        except UserProfile.DoesNotExist:
            user_language = 'EN'
    
    if query and len(query) >= 2:  # Start suggesting after 2 characters
        articles = Article.objects.filter(
            Q(title__icontains=query) | Q(summary__icontains=query),
            is_published=True,
            language=user_language
        )[:8]  # Limit to 8 suggestions
        
        suggestions = [{
            'id': article.id,
            'title': article.title,
            'slug': article.slug,
            'summary': article.summary[:100] if article.summary else '',
            'category': article.category.name if article.category else '',
        } for article in articles]
    
    return JsonResponse({'suggestions': suggestions})


# ============ HELPER FUNCTIONS ============
def check_achievements(user):
    """Check and award achievements to user"""
    progress = ReadingProgress.objects.filter(user=user)
    completed = progress.filter(is_completed=True).count()
    total_time = progress.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
    
    try:
        streak = ReadingStreak.objects.get(user=user)
        streak_days = streak.current_streak
    except ReadingStreak.DoesNotExist:
        streak_days = 0
    
    achievements = Achievement.objects.all()
    
    for achievement in achievements:
        # Check if already earned
        if UserAchievement.objects.filter(user=user, achievement=achievement).exists():
            continue
        
        earned = False
        
        if achievement.requirement_type == 'articles_read':
            earned = completed >= achievement.requirement_value
        elif achievement.requirement_type == 'streak_days':
            earned = streak_days >= achievement.requirement_value
        elif achievement.requirement_type == 'time_spent':
            earned = total_time >= achievement.requirement_value
        
        if earned:
            UserAchievement.objects.create(user=user, achievement=achievement)


def normalize_user_progress(user):
    """
    Normalize older progress rows so completed articles always stay at 100%.
    """
    ReadingProgress.objects.filter(
        user=user,
        is_completed=False,
        max_scroll_percentage__gte=90
    ).update(is_completed=True, max_scroll_percentage=100)

    ReadingProgress.objects.filter(
        user=user,
        is_completed=True,
        max_scroll_percentage__lt=100
    ).update(max_scroll_percentage=100)


def validate_reading_list_pin(pin):
    """Private reading lists use a 4-digit numeric PIN."""
    if not pin:
        return False, 'PIN is required for private reading lists.'
    if not pin.isdigit() or len(pin) != 4:
        return False, 'PIN must be exactly 4 digits.'
    return True, ''


# ============ API ENDPOINTS ============
@login_required
def get_user_stats(request):
    """API endpoint for user statistics"""
    normalize_user_progress(request.user)
    progress = ReadingProgress.objects.filter(user=request.user)
    
    stats = {
        'total_articles': progress.count(),
        'completed': progress.filter(is_completed=True).count(),
        'total_time': progress.aggregate(Sum('time_spent'))['time_spent__sum'] or 0,
        'total_notes': Note.objects.filter(user=request.user).count(),
        'total_bookmarks': Bookmark.objects.filter(user=request.user).count(),
    }
    
    return JsonResponse(stats)


# ============ NEW FEATURE VIEWS ============

@login_required
def my_progress(request):
    """View for tracking reading progress"""
    normalize_user_progress(request.user)
    progress_list = ReadingProgress.objects.filter(user=request.user).select_related('article', 'article__category')
    
    # Separate completed and in-progress
    completed = progress_list.filter(is_completed=True)
    in_progress = progress_list.filter(is_completed=False, scroll_percentage__gt=0)
    
    # Stats
    total_time = progress_list.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    
    context = {
        'completed': completed,
        'in_progress': in_progress,
        'total_completed': completed.count(),
        'total_in_progress': in_progress.count(),
        'total_hours': hours,
        'total_minutes': minutes,
    }
    return render(request, 'user/progress.html', context)


@login_required
def my_highlights(request):
    """View for all user highlights"""
    highlights = Highlight.objects.filter(user=request.user).select_related('article').order_by('-created_at')
    
    # Filter by article
    article_id = request.GET.get('article')
    if article_id:
        highlights = highlights.filter(article_id=article_id)
    
    # Filter by color
    color = request.GET.get('color')
    if color:
        highlights = highlights.filter(color=color)
    
    articles_with_highlights = Article.objects.filter(
        highlights__user=request.user
    ).distinct()
    
    context = {
        'highlights': highlights,
        'articles_with_highlights': articles_with_highlights,
        'colors': ['yellow', 'green', 'blue', 'pink', 'orange'],
    }
    return render(request, 'user/highlights.html', context)


@login_required
def my_streaks(request):
    """View for reading streaks"""
    streak, _ = ReadingStreak.objects.get_or_create(user=request.user)
    
    # Update streak if user is reading today
    today = timezone.now().date()
    if streak.last_read_date != today:
        # Check if we need to send milestone email
        if streak.current_streak in [7, 30, 100, 365]:
            send_streak_milestone_email(request.user, streak.current_streak)
    
    # Build reading history for calendar view.
    # `last_read_at` gets overwritten on the same progress row, so it cannot
    # represent all past active days by itself.
    reading_dates_set = set(
        ArticleViewLog.objects.filter(user=request.user)
        .values_list('viewed_at__date', flat=True)
        .distinct()
    )

    # Fall back to progress timestamps for any rows without view logs.
    progress_dates = ReadingProgress.objects.filter(user=request.user).values_list('last_read_at__date', flat=True)
    reading_dates_set.update(day for day in progress_dates if day)

    # Backfill consecutive days from the current streak so the week calendar
    # stays consistent with the shown streak count.
    if streak.last_read_date and streak.current_streak > 0:
        for offset in range(streak.current_streak):
            reading_dates_set.add(streak.last_read_date - timedelta(days=offset))

    reading_dates = sorted(day.isoformat() for day in reading_dates_set if day)
    
    # Build weekly calendar data (Monday to Sunday)
    # Get the start of the current week (Monday)
    days_since_monday = today.weekday()  # Monday = 0, Sunday = 6
    week_start = today - timedelta(days=days_since_monday)
    
    # Create list of days for the week with activity status
    week_days = []
    reading_dates_set = set(reading_dates)
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i]
        is_active = day.isoformat() in reading_dates_set
        is_today = day == today
        week_days.append({
            'name': day_name,
            'date': day.day,
            'full_date': day,
            'is_active': is_active,
            'is_today': is_today,
        })
    
    context = {
        'streak': streak,
        'reading_dates': json.dumps(reading_dates),
        'week_days': week_days,
    }
    return render(request, 'user/streaks.html', context)


@login_required
def my_achievements(request):
    """View for user achievements and badges"""
    user_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement')
    all_achievements = Achievement.objects.all()
    
    # Calculate progress for locked achievements
    progress = ReadingProgress.objects.filter(user=request.user)
    completed_articles = progress.filter(is_completed=True).count()
    total_time = progress.aggregate(Sum('time_spent'))['time_spent__sum'] or 0
    
    try:
        streak = ReadingStreak.objects.get(user=request.user)
        streak_days = streak.total_reading_days
    except ReadingStreak.DoesNotExist:
        streak_days = 0
    
    # Determine badge level
    badge_level = 'none'
    badge_color = '#9ca3af'
    if streak_days >= 150:
        badge_level = 'platinum'
        badge_color = '#e5e4e2'
    elif streak_days >= 90:
        badge_level = 'gold'
        badge_color = '#fbbf24'
    elif streak_days >= 30:
        badge_level = 'silver'
        badge_color = '#9ca3af'
    elif streak_days >= 7:
        badge_level = 'bronze'
        badge_color = '#cd7f32'
    
    earned_ids = [ua.achievement_id for ua in user_achievements]
    
    context = {
        'user_achievements': user_achievements,
        'all_achievements': all_achievements,
        'earned_ids': earned_ids,
        'completed_articles': completed_articles,
        'total_time': total_time,
        'streak_days': streak_days,
        'badge_level': badge_level,
        'badge_color': badge_color,
    }
    return render(request, 'user/achievements.html', context)


@login_required
def download_article_pdf(request, article_id):
    """Download article as PDF"""
    import re
    from html import unescape
    
    def strip_html_for_pdf(html_content):
        """Strip HTML tags and convert to plain text for PDF generation"""
        if not html_content:
            return ''
        
        # Replace <br>, <br/>, <br /> with newlines
        text = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
        
        # Replace </p> with double newlines for paragraph breaks
        text = re.sub(r'</p>', '\n\n', text, flags=re.IGNORECASE)
        
        # Remove all other HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Clean up multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
    
    article = get_object_or_404(Article, id=article_id)
    
    # Strip HTML from content for PDF
    clean_content = strip_html_for_pdf(article.content)
    
    if not REPORTLAB_AVAILABLE:
        # Fallback to plain text if reportlab not installed
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{article.slug}.txt"'
        response.write(f"{article.title}\n\n")
        response.write(f"Category: {article.category.name if article.category else 'N/A'}\n")
        response.write(f"Difficulty: {article.get_difficulty_display()}\n")
        response.write(f"Reading Time: {article.estimated_read_time} minutes\n\n")
        response.write("=" * 50 + "\n\n")
        response.write(clean_content)
        return response
    
    # Create PDF with reportlab
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
    )
    
    story = []
    story.append(Paragraph(article.title, title_style))
    story.append(Spacer(1, 12))
    
    meta_text = f"Category: {article.category.name if article.category else 'N/A'} | Difficulty: {article.get_difficulty_display()} | {article.estimated_read_time} min read"
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Add content paragraphs - use cleaned content
    content_paragraphs = clean_content.split('\n\n')
    for para in content_paragraphs:
        if para.strip():
            # Escape any remaining special XML characters for ReportLab
            safe_para = para.strip().replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            try:
                story.append(Paragraph(safe_para, styles['Normal']))
                story.append(Spacer(1, 12))
            except Exception as e:
                # If paragraph still fails, add as plain text
                story.append(Paragraph(safe_para.encode('ascii', 'ignore').decode('ascii'), styles['Normal']))
                story.append(Spacer(1, 12))
    
    doc.build(story)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{article.slug}.pdf"'
    return response


def send_streak_milestone_email(user, streak_days):
    """Send congratulations email for streak milestones"""
    subject = f'🎉 Congratulations! {streak_days} Day Reading Streak!'
    
    if streak_days == 7:
        message = f'''Hi {user.username},

Wow! You've maintained a 7-day reading streak! 🎉

You're building an excellent reading habit. Keep it up!

Your dedication to learning is inspiring. Here's to many more days of reading!

Happy Reading,
Smart Reader Team
'''
    elif streak_days == 30:
        message = f'''Hi {user.username},

AMAZING! 30 days of consistent reading! 🏆

You've earned the BRONZE badge! This is a significant achievement.

Your commitment to personal growth through reading is remarkable.

Keep pushing forward!

Happy Reading,
Smart Reader Team
'''
    elif streak_days == 100:
        message = f'''Hi {user.username},

INCREDIBLE! 100 days of reading! 🥇

You've earned the GOLD badge! You're now among our elite readers.

Your dedication is truly exceptional. You're an inspiration to the community!

Happy Reading,
Smart Reader Team
'''
    else:
        message = f'''Hi {user.username},

Congratulations on your {streak_days}-day reading streak!

Keep up the amazing work!

Happy Reading,
Smart Reader Team
'''
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@smartreader.com',
            [user.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Don't break the app if email fails


@login_required  
def quick_note(request):
    """Save a quick note (not attached to article)"""
    if request.method == 'POST':
        note_text = request.POST.get('note', '')
        
        if note_text:
            # Get or create a "Quick Notes" article placeholder
            quick_article, _ = Article.objects.get_or_create(
                slug='quick-notes-placeholder',
                defaults={
                    'title': 'Quick Notes',
                    'content': 'Placeholder for quick notes',
                    'is_published': False,
                }
            )
            
            Note.objects.create(
                user=request.user,
                article=quick_article,
                note=note_text,
                selected_text='Quick Note'
            )
            messages.success(request, 'Note saved!')
            
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))
    
    return redirect('dashboard')


@login_required
def remove_from_list(request, list_id, article_id):
    """Remove article from reading list"""
    reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
    article = get_object_or_404(Article, id=article_id)
    reading_list.articles.remove(article)
    messages.success(request, 'Article removed from list!')
    return redirect('reading_lists')


@login_required
def delete_reading_list(request, list_id):
    """Delete a reading list"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
    data = {}
    if request.headers.get('Content-Type', '').startswith('application/json'):
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            data = {}

    if reading_list.is_private:
        attempt, _ = ReadingListAccessAttempt.objects.get_or_create(
            user=request.user,
            reading_list=reading_list
        )

        if attempt.is_delete_locked():
            return JsonResponse({
                'status': 'locked',
                'message': 'Wrong PIN entered 3 times. Please try again after 24 hours.'
            }, status=403)

        pin = str(data.get('pin', '')).strip()
        is_valid_pin, pin_message = validate_reading_list_pin(pin)
        if not is_valid_pin:
            return JsonResponse({'status': 'error', 'message': pin_message}, status=400)

        if not reading_list.check_pin(pin):
            attempt.register_delete_failure()
            if attempt.is_delete_locked():
                return JsonResponse({
                    'status': 'locked',
                    'message': 'Wrong PIN entered 3 times. Please try again after 24 hours.'
                }, status=403)

            remaining_attempts = max(0, 3 - attempt.delete_failed_attempts)
            return JsonResponse({
                'status': 'error',
                'message': f'Incorrect PIN. {remaining_attempts} attempt(s) left.'
            }, status=403)

        attempt.register_delete_success()

    name = reading_list.name
    reading_list.delete()
    
    # Return JSON for AJAX to avoid page reload
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': f'Reading list "{name}" has been deleted.'})
    
    messages.success(request, 'Reading list deleted!')
    return redirect('reading_lists')


@login_required
def edit_reading_list(request, list_id):
    """Edit a reading list"""
    reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            is_public = data.get('is_public', False)
            new_pin = str(data.get('private_pin', data.get('access_pin', ''))).strip()
            current_pin = str(data.get('current_pin', '')).strip()
            verify_only = bool(data.get('verify_only', False))
            
            if verify_only:
                if reading_list.is_public:
                    return JsonResponse({'status': 'success', 'message': 'Public list does not need a PIN.'})

                attempt, _ = ReadingListAccessAttempt.objects.get_or_create(
                    user=request.user,
                    reading_list=reading_list
                )

                if attempt.is_locked():
                    return JsonResponse({
                        'status': 'locked',
                        'message': 'Wrong PIN entered 3 times. Please try again after 24 hours.'
                    }, status=403)

                is_valid_pin, pin_message = validate_reading_list_pin(current_pin)
                if not is_valid_pin:
                    return JsonResponse({'status': 'error', 'message': pin_message}, status=400)

                if not reading_list.check_pin(current_pin):
                    attempt.register_failure()
                    if attempt.is_locked():
                        return JsonResponse({
                            'status': 'locked',
                            'message': 'Wrong PIN entered 3 times. Please try again after 24 hours.'
                        }, status=403)

                    remaining_attempts = max(0, 3 - attempt.failed_attempts)
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Incorrect PIN. {remaining_attempts} attempt(s) left.'
                    }, status=403)

                attempt.register_success()
                return JsonResponse({'status': 'success', 'message': 'PIN verified.'})

            if not name:
                return JsonResponse({'status': 'error', 'message': 'List name is required.'})

            if reading_list.is_private:
                attempt, _ = ReadingListAccessAttempt.objects.get_or_create(
                    user=request.user,
                    reading_list=reading_list
                )

                if attempt.is_locked():
                    return JsonResponse({
                        'status': 'locked',
                        'message': 'Wrong PIN entered 3 times. Please try again after 24 hours.'
                    }, status=403)

                is_valid_pin, pin_message = validate_reading_list_pin(current_pin)
                if not is_valid_pin:
                    return JsonResponse({'status': 'error', 'message': pin_message}, status=400)

                if not reading_list.check_pin(current_pin):
                    attempt.register_failure()
                    if attempt.is_locked():
                        return JsonResponse({
                            'status': 'locked',
                            'message': 'Wrong PIN entered 3 times. Please try again after 24 hours.'
                        }, status=403)

                    remaining_attempts = max(0, 3 - attempt.failed_attempts)
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Incorrect PIN. {remaining_attempts} attempt(s) left.'
                    }, status=403)

                attempt.register_success()

            if not is_public:
                if new_pin:
                    is_valid_pin, pin_message = validate_reading_list_pin(new_pin)
                    if not is_valid_pin:
                        return JsonResponse({'status': 'error', 'message': pin_message})
                elif reading_list.is_public and not reading_list.access_pin:
                    return JsonResponse({'status': 'error', 'message': 'Private lists need a 4-digit PIN.'})
            
            reading_list.name = name
            reading_list.description = description
            reading_list.is_public = is_public
            if is_public:
                reading_list.access_pin = ''
            elif new_pin:
                reading_list.set_pin(new_pin)
            reading_list.save()
            
            return JsonResponse({'status': 'success', 'message': f'Reading list "{name}" has been updated.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# ============ ADMIN DASHBOARD ============
def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser or user.email in ADMIN_EMAILS


@login_required
def admin_dashboard(request):
    """Admin dashboard with analytics"""
    # Check if user is admin
    if not (request.user.is_staff or request.user.is_superuser or request.user.email in ADMIN_EMAILS):
        messages.error(request, 'You do not have admin privileges!')
        return redirect('dashboard')
    
    today = timezone.now().date()
    week_start = today - timedelta(days=6)
    registration_start = today - timedelta(days=29)
    
    # User Statistics
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__date__gte=today - timedelta(days=7)).count()
    active_users_today = SiteVisit.objects.filter(visit_date=today).values('user').distinct().count()
    
    # Article Statistics
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(is_published=True).count()
    total_views = Article.objects.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    # Today's visits
    visits_today = SiteVisit.objects.filter(visit_date=today).count()
    
    # Aggregate last 7 days visits in one query instead of one query per day.
    weekly_visit_counts = {
        item['visit_date']: item['count']
        for item in SiteVisit.objects
        .filter(visit_date__gte=week_start, visit_date__lte=today)
        .values('visit_date')
        .annotate(count=Count('id'))
    }
    visits_data = [
        {
            'date': day.strftime('%a'),
            'count': weekly_visit_counts.get(day, 0)
        }
        for day in (week_start + timedelta(days=i) for i in range(7))
    ]
    
    # Recent Articles (for admin dashboard)
    recent_articles = (
        Article.objects
        .select_related('category')
        .only('id', 'title', 'slug', 'created_at', 'category__name', 'views', 'is_published')
        .order_by('-created_at')[:5]
    )
    
    # Recent Users (for admin dashboard)
    recent_users = User.objects.only('id', 'username', 'first_name', 'email', 'date_joined', 'is_active').order_by('-date_joined')[:5]
    
    # Recent Activity
    recent_progress = (
        ReadingProgress.objects
        .select_related('user', 'article')
        .only(
            'id', 'last_read_at',
            'user__id', 'user__username', 'user__first_name',
            'article__id', 'article__title'
        )
        .order_by('-last_read_at')[:10]
    )
    
    # Aggregate last 30 days registrations in one query instead of one query per day.
    registration_counts = {
        item['date_joined__date']: item['count']
        for item in User.objects
        .filter(date_joined__date__gte=registration_start, date_joined__date__lte=today)
        .values('date_joined__date')
        .annotate(count=Count('id'))
    }
    registration_data = [
        {
            'date': day.strftime('%d %b'),
            'count': registration_counts.get(day, 0)
        }
        for day in (registration_start + timedelta(days=i) for i in range(30))
    ]
    
    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'active_users_today': active_users_today,
        'total_articles': total_articles,
        'published_articles': published_articles,
        'total_views': total_views,
        'visits_today': visits_today,
        'visits_data': json.dumps(visits_data),
        'recent_articles': recent_articles,
        'recent_users': recent_users,
        'recent_progress': recent_progress,
        'registration_data': json.dumps(registration_data),
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_users(request):
    """Admin view for managing users"""
    all_users = User.objects.all()
    users = all_users.order_by('-date_joined')
    admin_query = Q(is_staff=True) | Q(is_superuser=True) | Q(email__in=ADMIN_EMAILS)
    
    # Stats for the page
    total_users = all_users.count()
    active_users = all_users.filter(is_active=True).count()
    inactive_users = all_users.filter(is_active=False).count()
    admin_users_count = all_users.filter(admin_query).distinct().count()
    
    # Search
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'active':
        # Active regular users only (not staff/admin)
        users = users.filter(is_active=True).exclude(admin_query)
    elif status == 'deactive':
        # Deactivated users only
        users = users.filter(is_active=False)
    elif status == 'staff':
        # Staff and admins only
        users = users.filter(admin_query).distinct()
    
    # Pagination
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'search': search,
        'status': status,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'admin_users': admin_users_count,
        'admin_emails': ADMIN_EMAILS,
    }
    return render(request, 'admin/users.html', context)


@login_required
@user_passes_test(is_admin)
def admin_toggle_user_status(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user.is_superuser:
            messages.error(request, 'Cannot modify superuser status!')
        else:
            # Store previous status to check if it actually changed
            previous_status = user.is_active
            user.is_active = not user.is_active
            user.save()
            
            # Send email notification only if status actually changed
            if previous_status != user.is_active:
                status = 'activated' if user.is_active else 'deactivated'
                admin_user = request.user
                admin_name = admin_user.get_full_name() or admin_user.username
                admin_email = admin_user.email
                
                # Email notification
                subject = f'SmartReader Account {status.capitalize()} - Action Required'
                if user.is_active:
                    message = f"""Dear {user.first_name or user.username},

We are writing to inform you that your SmartReader account has been ACTIVATED.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACCOUNT STATUS: ACTIVE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Account Details:
• Username: {user.username}
• Email: {user.email}
• Status Changed: Active

Action Performed By:
• Administrator: {admin_name}
• Admin Email: {admin_email}

You can now log in and access all features of the platform.

Login URL: http://127.0.0.1:8000/login/

If you did not expect this change or have any questions, please contact our support team.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
SmartReader Administration Team

This is an automated message. Please do not reply directly to this email.
For support, contact: {admin_email}
"""
                else:
                    message = f"""Dear {user.first_name or user.username},

We are writing to inform you that your SmartReader account has been DEACTIVATED.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ACCOUNT STATUS: DEACTIVATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Account Details:
• Username: {user.username}
• Email: {user.email}
• Status Changed: Inactive

Action Performed By:
• Administrator: {admin_name}
• Admin Email: {admin_email}

You will not be able to log in until your account is reactivated by an administrator.

If you believe this action was taken in error or have any questions, please contact the administrator at {admin_email}.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Best regards,
SmartReader Administration Team

This is an automated message. Please do not reply directly to this email.
For support, contact: {admin_email}
"""
                
                try:
                    send_mail(
                        subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                    messages.success(request, f'User {user.username} has been {status} and notified via email.')
                except Exception as e:
                    messages.warning(request, f'User {user.username} has been {status}, but email notification failed: {str(e)}')
            else:
                messages.info(request, f'User status unchanged.')
                
    return redirect('admin_users')


@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    """Delete a user"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        if user.is_superuser:
            messages.error(request, 'Cannot delete superuser!')
        elif user == request.user:
            messages.error(request, 'Cannot delete yourself!')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'User {username} has been deleted.')
    return redirect('admin_users')


@login_required
@user_passes_test(is_admin)
def admin_articles(request):
    """Admin view for managing articles"""
    all_articles = Article.objects.all()
    articles = all_articles.order_by('-created_at')
    categories = Category.objects.all()
    
    # Stats for the page
    total_articles = all_articles.count()
    published_articles = all_articles.filter(is_published=True).count()
    draft_articles = all_articles.filter(is_published=False).count()
    total_views = all_articles.aggregate(Sum('views_count'))['views_count__sum'] or 0
    
    # Search
    search = request.GET.get('search', '')
    if search:
        articles = articles.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search)
        )
    
    # Filter by category
    category_id = request.GET.get('category', '')
    if category_id:
        articles = articles.filter(category_id=category_id)
    
    # Filter by status
    status = request.GET.get('status', '')
    if status == 'published':
        articles = articles.filter(is_published=True)
    elif status == 'draft':
        articles = articles.filter(is_published=False)
    elif status == 'featured':
        articles = articles.filter(is_featured=True)
    
    # Pagination
    paginator = Paginator(articles, 20)
    page = request.GET.get('page')
    articles = paginator.get_page(page)
    
    context = {
        'articles': articles,
        'categories': categories,
        'search': search,
        'category_id': category_id,
        'status': status,
        'total_articles': total_articles,
        'published_articles': published_articles,
        'draft_articles': draft_articles,
        'total_views': total_views,
    }
    return render(request, 'admin/articles.html', context)


@login_required
@user_passes_test(is_admin)
def admin_add_article(request):
    """Add new article"""
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        summary = request.POST.get('summary', '')
        category_id = request.POST.get('category')
        difficulty = request.POST.get('difficulty', 'beginner')
        is_featured = request.POST.get('is_featured') == 'on'
        is_published = request.POST.get('is_published') == 'on'
        tag_ids = request.POST.getlist('tags')
        
        article = Article.objects.create(
            title=title,
            content=content,
            summary=summary,
            category_id=category_id if category_id else None,
            difficulty=difficulty,
            is_featured=is_featured,
            is_published=is_published,
            author=request.user
        )
        
        if tag_ids:
            article.tags.set(tag_ids)
        
        # Handle cover image
        if 'cover_image' in request.FILES:
            article.cover_image = request.FILES['cover_image']
            article.save()
        
        messages.success(request, f'Article "{title}" has been created.')
        return redirect('admin_articles')
    
    context = {
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'admin/add_article.html', context)


@login_required
@user_passes_test(is_admin)
def admin_edit_article(request, article_id):
    """Edit article"""
    article = get_object_or_404(Article, id=article_id)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.content = request.POST.get('content')
        article.summary = request.POST.get('summary', '')
        article.category_id = request.POST.get('category') or None
        article.difficulty = request.POST.get('difficulty', 'beginner')
        article.is_featured = request.POST.get('is_featured') == 'on'
        article.is_published = request.POST.get('is_published') == 'on'
        
        tag_ids = request.POST.getlist('tags')
        article.tags.set(tag_ids)
        
        # Handle cover image
        if 'cover_image' in request.FILES:
            article.cover_image = request.FILES['cover_image']
        
        article.save()
        messages.success(request, f'Article "{article.title}" has been updated.')
        return redirect('admin_articles')
    
    context = {
        'article': article,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'admin/edit_article.html', context)


@login_required
@user_passes_test(is_admin)
def admin_delete_article(request, article_id):
    """Delete article"""
    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)
        title = article.title
        article.delete()
        
        # Return JSON for AJAX to avoid page reload
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f'Article "{title}" has been deleted.'})
        
        messages.success(request, f'Article "{title}" has been deleted.')
    return redirect('admin_articles')


@login_required
@user_passes_test(is_admin)
def admin_analytics(request):
    """Detailed analytics page"""
    today = timezone.now().date()
    
    # Time period filter
    period = request.GET.get('period', '7')
    try:
        days = int(period)
    except:
        days = 7
    
    start_date = today - timedelta(days=days-1)
    
    # Daily visits
    daily_visits = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        count = SiteVisit.objects.filter(visit_date=day).count()
        unique_users = SiteVisit.objects.filter(visit_date=day).values('user').distinct().count()
        daily_visits.append({
            'date': day.strftime('%d %b'),
            'visits': count,
            'unique': unique_users
        })
    
    # Total visits and article views
    total_visits = SiteVisit.objects.filter(visit_date__gte=start_date).count()
    total_article_views = ArticleViewLog.objects.filter(viewed_at__date__gte=start_date).count()
    
    # Article analytics - Top 10 only
    article_views = ArticleViewLog.objects.filter(
        viewed_at__date__gte=start_date
    ).values('article__title').annotate(
        views=Count('id'),
        total_time=Sum('time_spent')
    ).order_by('-views')[:10]
    
    # User engagement
    active_readers = ReadingProgress.objects.filter(
        last_read_at__date__gte=start_date
    ).values('user').distinct().count()
    
    completed_articles = ReadingProgress.objects.filter(
        last_read_at__date__gte=start_date,
        is_completed=True
    ).count()
    
    # New user registrations in the period
    new_users = User.objects.filter(date_joined__date__gte=start_date).count()
    
    # Total users
    total_users = User.objects.count()
    
    # Active users (users who visited in the period)
    active_users = SiteVisit.objects.filter(
        visit_date__gte=start_date,
        user__isnull=False
    ).values('user').distinct().count()
    
    # Daily user registrations
    daily_registrations = []
    for i in range(days):
        day = start_date + timedelta(days=i)
        count = User.objects.filter(date_joined__date=day).count()
        daily_registrations.append({
            'date': day.strftime('%d %b'),
            'registrations': count
        })
    
    # Top active users - Top 1 only (compact view, change to 3 when more users)
    top_users = SiteVisit.objects.filter(
        visit_date__gte=start_date,
        user__isnull=False
    ).values(
        'user__username',
        'user__email'
    ).annotate(
        visit_count=Count('id')
    ).order_by('-visit_count')[:1]
    
    # Category distribution - Top 10 only
    category_stats = Article.objects.values('category__name').annotate(
        count=Count('id'),
        views=Sum('views_count')
    ).order_by('-views')[:10]
    
    # User engagement stats
    total_reading_time = ArticleViewLog.objects.filter(
        viewed_at__date__gte=start_date
    ).aggregate(total=Sum('time_spent'))['total'] or 0
    
    # Average reading time per user
    avg_reading_time = total_reading_time // max(active_readers, 1)
    
    # Recent registrations (last 5 users)
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Unique project-specific stats
    total_highlights = Highlight.objects.count()
    total_notes = Note.objects.count()
    total_feedbacks = Feedback.objects.count()
    total_ratings = Rating.objects.count()
    
    # Average rating across all articles
    from django.db.models import Avg
    avg_rating = Rating.objects.aggregate(avg=Avg('score'))['avg'] or 0
    
    # Achievements earned
    total_achievements = UserAchievement.objects.count()
    
    # Reading lists created
    total_reading_lists = ReadingList.objects.count()
    
    # Top rated articles (for display)
    top_rated_articles = Article.objects.annotate(
        avg_score=Avg('ratings__score'),
        rating_count=Count('ratings')
    ).filter(rating_count__gt=0).order_by('-avg_score')[:3]
    
    # Most bookmarked articles
    most_bookmarked = Article.objects.annotate(
        bookmark_count=Count('bookmarks')
    ).filter(bookmark_count__gt=0).order_by('-bookmark_count')[:5]
    
    # Article difficulty distribution
    difficulty_stats = Article.objects.values('difficulty').annotate(
        count=Count('id')
    ).order_by('difficulty')
    
    # Reading progress stats
    in_progress_reads = ReadingProgress.objects.filter(is_completed=False).count()
    completed_reads = ReadingProgress.objects.filter(is_completed=True).count()
    total_reads = in_progress_reads + completed_reads
    completion_rate = round((completed_reads / total_reads * 100) if total_reads > 0 else 0)
    
    context = {
        'period': period,
        'daily_visits': json.dumps(daily_visits),
        'daily_registrations': json.dumps(daily_registrations),
        'article_views': article_views,
        'active_readers': active_readers,
        'completed_articles': completed_articles,
        'category_stats': category_stats,
        'total_visits': total_visits,
        'total_article_views': total_article_views,
        'new_users': new_users,
        'total_users': total_users,
        'active_users': active_users,
        'top_users': top_users,
        'total_reading_time': total_reading_time,
        'avg_reading_time': avg_reading_time,
        'recent_users': recent_users,
        'total_highlights': total_highlights,
        'total_notes': total_notes,
        'total_feedbacks': total_feedbacks,
        'total_ratings': total_ratings,
        'avg_rating': round(avg_rating, 1),
        'total_achievements': total_achievements,
        'total_reading_lists': total_reading_lists,
        'top_rated_articles': top_rated_articles,
        'most_bookmarked': most_bookmarked,
        'difficulty_stats': difficulty_stats,
        'in_progress_reads': in_progress_reads,
        'completed_reads': completed_reads,
        'completion_rate': completion_rate,
    }
    return render(request, 'admin/analytics.html', context)


# Middleware function to track visits
def track_visit(request):
    """Track site visits - call this from middleware or views"""
    if not request.path.startswith('/admin/') and not request.path.startswith('/static/'):
        SiteVisit.objects.create(
            user=request.user if request.user.is_authenticated else None,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            page_visited=request.path
        )


# ============ FEEDBACK ============
@login_required
def submit_feedback(request):
    """Submit feedback for an article"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            article_id = data.get('article_id')
            feedback_text = data.get('feedback_text', '').strip()
            is_helpful = data.get('is_helpful', True)
            
            if not feedback_text:
                return JsonResponse({'status': 'error', 'message': 'Feedback text is required'})
            
            article = get_object_or_404(Article, id=article_id)
            
            Feedback.objects.create(
                user=request.user,
                article=article,
                feedback_text=feedback_text,
                is_helpful=is_helpful
            )
            
            return JsonResponse({'status': 'success', 'message': 'Thanks for your valuable feedback! We appreciate your input.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required
def my_feedbacks(request):
    """View user's submitted feedbacks"""
    feedbacks = Feedback.objects.filter(user=request.user).select_related('article').order_by('-created_at')
    
    context = {
        'feedbacks': feedbacks,
        'total_feedbacks': feedbacks.count(),
    }
    return render(request, 'user/feedbacks.html', context)


@login_required
@user_passes_test(is_admin)
def admin_feedbacks(request):
    """Admin view for managing feedbacks"""
    feedbacks = Feedback.objects.select_related('user', 'article').order_by('-created_at')
    
    # Filter by article
    article_id = request.GET.get('article')
    if article_id:
        feedbacks = feedbacks.filter(article_id=article_id)
    
    # Filter by helpful/not helpful
    helpful = request.GET.get('helpful')
    if helpful == 'yes':
        feedbacks = feedbacks.filter(is_helpful=True)
    elif helpful == 'no':
        feedbacks = feedbacks.filter(is_helpful=False)
    
    # Get articles with feedback counts
    articles_with_feedback = Article.objects.annotate(
        feedback_count=Count('feedbacks')
    ).filter(feedback_count__gt=0).order_by('-feedback_count')
    
    # Pagination
    paginator = Paginator(feedbacks, 20)
    page = request.GET.get('page')
    feedbacks = paginator.get_page(page)
    
    context = {
        'feedbacks': feedbacks,
        'articles_with_feedback': articles_with_feedback,
        'selected_article': article_id,
        'selected_helpful': helpful,
    }
    return render(request, 'admin/feedbacks.html', context)


# ============ LANGUAGE & THEME SWITCHING ============
@login_required
def change_language(request):
    """Change user's language preference"""
    if request.method == 'POST':
        language = request.POST.get('language', 'EN').upper()
        if language:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.preferred_language = language
            profile.save()
            
            # Activate language for current session (convert to lowercase for Django translation)
            translation.activate(language.lower())
            request.session[translation.LANGUAGE_SESSION_KEY] = language.lower()
            
            messages.success(request, 'Language preference updated successfully! 🌍')
    
    return redirect(request.META.get('HTTP_REFERER', 'profile'))


@login_required
def change_theme(request):
    """Change user's theme preference"""
    if request.method == 'POST':
        theme = request.POST.get('theme')
        if theme in ['light', 'dark']:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.theme = theme
            profile.save()
            
            # Return JSON for AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', ''):
                return JsonResponse({'status': 'success', 'theme': theme})
            
            messages.success(request, f'Theme changed to {theme} mode! 🎨')
    
    return redirect(request.META.get('HTTP_REFERER', 'profile'))
