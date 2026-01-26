import json
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
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

from .models import (
    Article, ReadingProgress, Note, UserProfile, Category, Tag,
    Bookmark, Highlight, Rating, ReadingStreak, Achievement, 
    UserAchievement, ReadingList, OTPVerification, SiteVisit, ArticleViewLog, Feedback
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


# ============ HOME ============
def home(request):
    featured_articles = Article.objects.filter(is_featured=True, is_published=True)[:3]
    recent_articles = Article.objects.filter(is_published=True)[:6]
    
    # Show 28 popular categories on home page
    popular_category_slugs = [
        'technology', 'science', 'business', 'health-wellness',
        'art-design', 'programming', 'finance', 'personal-development',
        'artificial-intelligence', 'data-science', 'web-development', 'cybersecurity',
        'psychology', 'history', 'literature', 'music',
        'photography', 'entrepreneurship', 'marketing', 'leadership',
        'cooking-recipes', 'travel', 'sports-fitness', 'yoga-meditation',
        'physics', 'biology', 'astronomy', 'mathematics'
    ]
    categories = Category.objects.filter(slug__in=popular_category_slugs)[:28]
    
    # Stats for homepage - Display as 100,000+ for impressive look
    total_articles = Article.objects.filter(is_published=True).count()
    display_articles = "100,000" if total_articles > 0 else "0"
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

def validate_email_format(email):
    """Validate email format"""
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def send_otp_email(email, otp):
    """Send OTP to user's email - Optimized for speed and reliability"""
    import time
    start_time = time.time()
    
    print(f"\n🔍 DEBUG: send_otp_email() function called")
    print(f"   Target email: {email}")
    print(f"   OTP: {otp}")
    
    subject = 'SmartReader - Email Verification OTP'
    message = f'''Hello!

Your OTP for SmartReader registration is: {otp}

This OTP will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
SmartReader Team
'''
    html_message = f'''
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background: #f3f4f6;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="color: #6366f1; text-align: center; margin-bottom: 10px;">📚 SmartReader</h2>
            <p style="color: #666;">Hello!</p>
            <p style="color: #666;">Your OTP for email verification is:</p>
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-size: 36px; font-weight: bold; text-align: center; padding: 25px; border-radius: 8px; letter-spacing: 10px; margin: 25px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                {otp}
            </div>
            <p style="color: #666;">This OTP will expire in <strong>10 minutes</strong>.</p>
            <p style="color: #999; font-size: 12px;">If you didn't request this, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
            <p style="color: #9ca3af; font-size: 12px; text-align: center;">SmartReader Team</p>
        </div>
    </body>
    </html>
    '''
    try:
        from django.core.mail import EmailMultiAlternatives
        from_email = settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@smartreader.com'
        
        print(f"✓ Creating email message")
        print(f"   From: {from_email}")
        print(f"   To: {email}")
        print(f"   Subject: {subject}")
        print(f"   Backend: {settings.EMAIL_BACKEND}")
        print(f"   USE_REAL_EMAIL: {getattr(settings, 'USE_REAL_EMAIL', False)}")
        
        email_msg = EmailMultiAlternatives(subject, message, from_email, [email])
        email_msg.attach_alternative(html_message, "text/html")
        
        print(f"🔄 Sending email (timeout: 15 seconds)...")
        
        # Send email with improved error handling
        email_msg.send(fail_silently=False)
        
        elapsed = time.time() - start_time
        print(f"✅ EMAIL SENT SUCCESSFULLY in {elapsed:.2f} seconds!")
        return True
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Email sending error after {elapsed:.2f} seconds: {e}")
        import traceback
        traceback.print_exc()
        
        # In debug mode, still allow OTP flow to work
        if settings.DEBUG:
            print(f"\n⚠️  [DEBUG MODE] Email failed but OTP is still valid")
            print(f"   ✓ OTP {otp} for {email} saved in database")
            print(f"   ✓ Check terminal for OTP or fix email configuration")
            return True  # Return True so user can still proceed
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
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                print(f"❌ Email already registered: {email}")
                return JsonResponse({'status': 'error', 'message': 'Email already registered'})
            
            # Admin emails don't need OTP - auto verify
            if email in ADMIN_EMAILS:
                print(f"✓ Admin email detected: {email}")
                return JsonResponse({'status': 'admin', 'message': 'Admin email - OTP not required'})
            
            # Generate OTP
            otp = OTPVerification.generate_otp()
            expires_at = timezone.now() + timedelta(minutes=10)
            
            print(f"✓ OTP generated: {otp}")
            
            # Delete old OTPs for this email
            deleted_count = OTPVerification.objects.filter(email=email).delete()
            print(f"✓ Deleted {deleted_count[0]} old OTP records")
            
            # Create new OTP record in database
            otp_record = OTPVerification.objects.create(
                email=email,
                otp=otp,
                expires_at=expires_at
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
            
            # Determine appropriate message based on email configuration
            use_real_email = getattr(settings, 'USE_REAL_EMAIL', False)
            
            if email_sent:
                if use_real_email:
                    # Real email sent - user should check inbox
                    message = f'✓ OTP sent to {email} in {send_elapsed:.1f}s! Check your inbox and spam folder.'
                else:
                    # Console mode - OTP printed to terminal
                    message = f'✓ OTP generated! Check the server terminal/console for OTP: {otp}'
                
                return JsonResponse({
                    'status': 'success',
                    'message': message,
                    'sent_time': f'{send_elapsed:.1f}s',
                    'debug_otp': otp if settings.DEBUG and not use_real_email else None  # Show OTP in console mode only
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
                otp_record = OTPVerification.objects.filter(email=email, otp=otp).latest('created_at')
                
                if otp_record.is_expired():
                    print(f"[OTP VERIFY] OTP expired for {email}")
                    return JsonResponse({'status': 'error', 'message': 'OTP has expired. Please request a new one.'})
                
                if otp_record.is_verified:
                    # Already verified is okay - user can proceed
                    print(f"[OTP VERIFY] OTP already verified for {email}")
                    return JsonResponse({'status': 'success', 'message': 'Email already verified'})
                
                # Mark as verified
                otp_record.is_verified = True
                otp_record.save()
                
                print(f"[OTP VERIFY] ✓ OTP verified successfully for {email}")
                return JsonResponse({'status': 'success', 'message': 'Email verified successfully!'})
            
            except OTPVerification.DoesNotExist:
                print(f"[OTP VERIFY] Invalid OTP '{otp}' for {email}")
                return JsonResponse({'status': 'error', 'message': 'Invalid OTP. Please check and try again.'})
                
        except Exception as e:
            print(f"[OTP VERIFY] Error: {e}")
            return JsonResponse({'status': 'error', 'message': 'Error verifying OTP'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


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
            # Verify OTP for regular users
            try:
                otp_record = OTPVerification.objects.filter(email=email, otp=otp, is_verified=True).latest('created_at')
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
    articles = Article.objects.filter(is_published=True)
    # Limit categories and tags shown - only top 8 categories and 15 tags
    categories = Category.objects.annotate(article_count=Count('articles')).order_by('-article_count')[:8]
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
    
    # Get related articles
    related_articles = Article.objects.filter(
        category=article.category, is_published=True
    ).exclude(id=article.id)[:4]
    
    # Get ratings
    avg_rating = article.ratings.aggregate(Avg('score'))['score__avg'] or 0
    rating_count = article.ratings.count()
    
    # User-specific data
    is_bookmarked = False
    user_rating = None
    user_notes = []
    user_highlights = []
    progress = None
    
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(user=request.user, article=article).exists()
        user_rating = Rating.objects.filter(user=request.user, article=article).first()
        user_notes = Note.objects.filter(user=request.user, article=article)
        user_highlights = Highlight.objects.filter(user=request.user, article=article)
        progress, _ = ReadingProgress.objects.get_or_create(
            user=request.user, article=article
        )
        
        # Update reading streak
        streak, _ = ReadingStreak.objects.get_or_create(user=request.user)
        if streak.last_read_date != timezone.now().date():
            streak.update_streak()
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'avg_rating': avg_rating,
        'rating_count': rating_count,
        'is_bookmarked': is_bookmarked,
        'user_rating': user_rating,
        'user_notes': user_notes,
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
            was_just_completed = True
        
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
        
        profile = UserProfile.objects.get(user=request.user)
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
        data = json.loads(request.body)
        article_id = data.get('article_id')
        
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            article_id=article_id
        )
        
        if not created:
            bookmark.delete()
            return JsonResponse({'status': 'removed'})
        
        return JsonResponse({'status': 'added'})
    
    return JsonResponse({'status': 'error'}, status=400)


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
        profile.preferred_font_size = int(request.POST.get('font_size', 16))
        profile.dark_mode = request.POST.get('dark_mode') == 'on'
        profile.save()
        
        # Update user info
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'user/profile.html', context)


# ============ READING LISTS ============
@login_required
def reading_lists(request):
    lists = ReadingList.objects.filter(user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        is_public = request.POST.get('is_public') == 'on'
        
        if name:
            ReadingList.objects.create(
                user=request.user,
                name=name,
                description=description,
                is_public=is_public
            )
            messages.success(request, 'Reading list created!')
    
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


# ============ SEARCH ============
def search(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Article.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(tags__name__icontains=query)
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
    
    if query and len(query) >= 2:  # Start suggesting after 2 characters
        articles = Article.objects.filter(
            Q(title__icontains=query) | Q(summary__icontains=query),
            is_published=True
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


# ============ API ENDPOINTS ============
@login_required
def get_user_stats(request):
    """API endpoint for user statistics"""
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
    
    # Get reading history for calendar view
    progress = ReadingProgress.objects.filter(user=request.user)
    reading_days = progress.values('last_read_at__date').distinct()
    reading_dates = [r['last_read_at__date'].isoformat() for r in reading_days if r['last_read_at__date']]
    
    context = {
        'streak': streak,
        'reading_dates': json.dumps(reading_dates),
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
    article = get_object_or_404(Article, id=article_id)
    
    if not REPORTLAB_AVAILABLE:
        # Fallback to plain text if reportlab not installed
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{article.slug}.txt"'
        response.write(f"{article.title}\n\n")
        response.write(f"Category: {article.category.name if article.category else 'N/A'}\n")
        response.write(f"Difficulty: {article.get_difficulty_display()}\n")
        response.write(f"Reading Time: {article.estimated_read_time} minutes\n\n")
        response.write("=" * 50 + "\n\n")
        response.write(article.content)
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
    
    # Add content paragraphs
    content_paragraphs = article.content.split('\n\n')
    for para in content_paragraphs:
        if para.strip():
            story.append(Paragraph(para.strip(), styles['Normal']))
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
    reading_list = get_object_or_404(ReadingList, id=list_id, user=request.user)
    reading_list.delete()
    messages.success(request, 'Reading list deleted!')
    return redirect('reading_lists')


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
    
    # Last 7 days visits for chart
    visits_data = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = SiteVisit.objects.filter(visit_date=day).count()
        visits_data.append({
            'date': day.strftime('%a'),
            'count': count
        })
    
    # Top Articles (by views)
    top_articles = Article.objects.filter(is_published=True).order_by('-views_count')[:10]
    
    # Recent Articles (for admin dashboard)
    recent_articles = Article.objects.all().order_by('-created_at')[:5]
    
    # Recent Users (for admin dashboard)
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    
    # Recent Activity
    recent_progress = ReadingProgress.objects.select_related('user', 'article').order_by('-last_read_at')[:10]
    
    # User Registration Trend (last 30 days)
    registration_data = []
    for i in range(30):
        day = today - timedelta(days=29-i)
        count = User.objects.filter(date_joined__date=day).count()
        registration_data.append({
            'date': day.strftime('%d %b'),
            'count': count
        })
    
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
        'top_articles': top_articles,
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
    
    # Stats for the page
    total_users = all_users.count()
    active_users = all_users.filter(is_active=True).count()
    inactive_users = all_users.filter(is_active=False).count()
    admin_users_count = all_users.filter(Q(is_staff=True) | Q(is_superuser=True)).count()
    
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
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    elif status == 'staff':
        users = users.filter(is_staff=True)
    
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
            user.is_active = not user.is_active
            user.save()
            status = 'activated' if user.is_active else 'deactivated'
            messages.success(request, f'User {user.username} has been {status}.')
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
    
    # Article analytics
    article_views = ArticleViewLog.objects.filter(
        viewed_at__date__gte=start_date
    ).values('article__title').annotate(
        views=Count('id'),
        total_time=Sum('time_spent')
    ).order_by('-views')[:20]
    
    # User engagement
    active_readers = ReadingProgress.objects.filter(
        last_read_at__date__gte=start_date
    ).values('user').distinct().count()
    
    completed_articles = ReadingProgress.objects.filter(
        last_read_at__date__gte=start_date,
        is_completed=True
    ).count()
    
    # Category distribution
    category_stats = Article.objects.values('category__name').annotate(
        count=Count('id'),
        views=Sum('views_count')
    ).order_by('-views')
    
    context = {
        'period': period,
        'daily_visits': json.dumps(daily_visits),
        'article_views': article_views,
        'active_readers': active_readers,
        'completed_articles': completed_articles,
        'category_stats': category_stats,
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
            
            return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


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
        language = request.POST.get('language')
        if language:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            profile.language = language
            profile.save()
            
            # Activate language for current session
            translation.activate(language)
            request.session[translation.LANGUAGE_SESSION_KEY] = language
            
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
            
            messages.success(request, f'Theme changed to {theme} mode! 🎨')
    
    return redirect(request.META.get('HTTP_REFERER', 'profile'))
