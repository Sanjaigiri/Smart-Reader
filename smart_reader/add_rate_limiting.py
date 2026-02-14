"""
Rate Limiting Fix for OTP Requests
===================================
This adds rate limiting to prevent OTP spam.

Add this code to your views.py send_otp function.
"""

from django.core.cache import cache
from datetime import timedelta

def send_otp_with_rate_limiting(request):
    """Send OTP to email for verification - WITH RATE LIMITING"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            # ====== RATE LIMITING - ADD THIS ======
            # Check if OTP was sent recently (within last 60 seconds)
            rate_limit_key = f'otp_rate_limit_{email}'
            last_sent = cache.get(rate_limit_key)
            
            if last_sent:
                return JsonResponse({
                    'status': 'error',
                    'message': '⏱️ Please wait 60 seconds before requesting another OTP'
                })
            
            # Check daily limit (max 5 OTPs per email per day)
            daily_limit_key = f'otp_daily_limit_{email}_{timezone.now().date()}'
            daily_count = cache.get(daily_limit_key, 0)
            
            if daily_count >= 5:
                return JsonResponse({
                    'status': 'error',
                    'message': '🚫 Maximum OTP limit reached for today. Please try again tomorrow.'
                })
            # ====== END RATE LIMITING ======
            
            print(f"\n{'='*60}")
            print(f"🔍 DEBUG: send_otp() function called")
            print(f"   Email received: {email}")
            print(f"{'='*60}\n")
            
            # Validate email format
            if not validate_email_format(email):
                print(f"❌ Email validation failed for: {email}")
                return JsonResponse({'status': 'error', 'message': 'Invalid email format'})
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                print(f"❌ Email already registered: {email}")
                return JsonResponse({'status': 'error', 'message': 'Email already registered'})
            
            # Generate OTP
            otp = OTPVerification.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Delete old OTPs for this email
            OTPVerification.objects.filter(email=email).delete()
            
            # Create new OTP record in database
            otp_record = OTPVerification.objects.create(
                email=email,
                otp=otp,
                expires_at=expires_at
            )
            
            # Send OTP email
            email_sent = send_otp_email(email, otp)
            
            if email_sent:
                # ====== SET RATE LIMITS - ADD THIS ======
                # Set 60-second rate limit
                cache.set(rate_limit_key, True, 60)
                
                # Increment daily counter (expires at midnight)
                cache.set(daily_limit_key, daily_count + 1, 86400)  # 24 hours
                # ====== END SET RATE LIMITS ======
                
                use_real_email = getattr(settings, 'USE_REAL_EMAIL', False)
                
                if use_real_email:
                    message = f'✓ OTP sent to {email}! Check your inbox and spam folder.'
                else:
                    message = f'✓ OTP generated! Check the server terminal/console for OTP: {otp}'
                
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'debug_otp': otp if settings.DEBUG and not use_real_email else None
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to send OTP. Please check email configuration.'
                })
                
        except Exception as e:
            print(f"\n❌ ERROR in send_otp: {e}")
            return JsonResponse({'status': 'error', 'message': f'Failed to send OTP: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# ====== ADDITIONAL: Add resend OTP with countdown ======
def check_otp_cooldown(request):
    """Check if user can request OTP (for displaying countdown)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '').strip().lower()
            
            rate_limit_key = f'otp_rate_limit_{email}'
            
            # Check remaining time
            ttl = cache.ttl(rate_limit_key)  # Time to live in seconds
            
            if ttl > 0:
                return JsonResponse({
                    'status': 'waiting',
                    'remaining_seconds': ttl,
                    'message': f'Please wait {ttl} seconds'
                })
            else:
                return JsonResponse({
                    'status': 'ready',
                    'message': 'You can request OTP now'
                })
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


# ====== JavaScript for frontend (add to register.html) ======
FRONTEND_JS = """
<script>
let otpCooldown = 0;
let cooldownInterval;

function startOTPCooldown(seconds) {
    otpCooldown = seconds;
    const sendOtpBtn = document.getElementById('sendOtpBtn');
    
    if (cooldownInterval) {
        clearInterval(cooldownInterval);
    }
    
    cooldownInterval = setInterval(() => {
        if (otpCooldown > 0) {
            sendOtpBtn.textContent = `Resend OTP (${otpCooldown}s)`;
            sendOtpBtn.disabled = true;
            otpCooldown--;
        } else {
            sendOtpBtn.textContent = 'Send OTP';
            sendOtpBtn.disabled = false;
            clearInterval(cooldownInterval);
        }
    }, 1000);
}

// After successful OTP send:
if (data.status === 'success') {
    startOTPCooldown(60);  // 60 second cooldown
}
</script>
"""

print(FRONTEND_JS)
