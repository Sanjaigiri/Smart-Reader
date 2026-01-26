"""
Database Records Viewer
This script connects to the smart_reader database and displays all records
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.contrib.auth.models import User
from reader.models import (
    UserProfile, OTPVerification, Article, Category, Tag,
    ReadingProgress, Bookmark, Highlight, Note, Rating,
    Feedback, ReadingStreak, Achievement, UserAchievement,
    ReadingList, SiteVisit, ArticleViewLog
)


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)


def view_users():
    """Display all users and their profiles"""
    print_section("USERS & PROFILES")
    
    users = User.objects.all()
    if not users:
        print("No users found.")
        return
    
    for user in users:
        print(f"\n{'─'*80}")
        print(f"ID: {user.id}")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Full Name: {user.first_name} {user.last_name}")
        print(f"Is Superuser/Admin: {'Yes' if user.is_superuser else 'No'}")
        print(f"Is Staff: {'Yes' if user.is_staff else 'No'}")
        print(f"Is Active: {'Yes' if user.is_active else 'No'}")
        print(f"Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
        
        # Profile information
        try:
            profile = user.profile
            print(f"\nProfile Information:")
            print(f"  Bio: {profile.bio[:100] if profile.bio else 'N/A'}...")
            print(f"  Reading Goal: {profile.reading_goal} articles/week")
            print(f"  Email Verified: {'Yes' if profile.is_email_verified else 'No'}")
            print(f"  Language: {profile.get_language_display()}")
            print(f"  Theme: {profile.get_theme_display()}")
            print(f"  Dark Mode: {'Yes' if profile.dark_mode else 'No'}")
            print(f"  Font Size: {profile.preferred_font_size}px")
        except UserProfile.DoesNotExist:
            print(f"\nProfile Information: No profile found")


def view_admins():
    """Display admin users"""
    print_section("ADMIN USERS")
    
    admins = User.objects.filter(is_superuser=True) | User.objects.filter(is_staff=True)
    if not admins:
        print("No admin users found.")
        return
    
    for admin in admins:
        print(f"\n{'─'*80}")
        print(f"ID: {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Email: {admin.email}")
        print(f"Full Name: {admin.first_name} {admin.last_name}")
        print(f"Is Superuser: {'Yes' if admin.is_superuser else 'No'}")
        print(f"Is Staff: {'Yes' if admin.is_staff else 'No'}")
        print(f"Date Joined: {admin.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Last Login: {admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if admin.last_login else 'Never'}")


def view_signup_login_details():
    """Display signup and login statistics"""
    print_section("SIGNUP & LOGIN DETAILS")
    
    users = User.objects.all()
    if not users:
        print("No signup records found.")
        return
    
    print(f"\nTotal Registered Users: {users.count()}")
    print(f"Active Users: {users.filter(is_active=True).count()}")
    print(f"Inactive Users: {users.filter(is_active=False).count()}")
    
    # OTP Verifications
    print(f"\n{'─'*80}")
    print("OTP VERIFICATION RECORDS:")
    otps = OTPVerification.objects.all()
    if otps:
        print(f"Total OTP Records: {otps.count()}")
        print(f"Verified: {otps.filter(is_verified=True).count()}")
        print(f"Pending/Expired: {otps.filter(is_verified=False).count()}")
        
        print("\nRecent OTP Verifications:")
        for otp in otps[:10]:
            status = "✓ Verified" if otp.is_verified else "✗ Pending"
            print(f"  {otp.email} - {otp.otp} - {status} - {otp.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("No OTP records found.")
    
    # Recent Logins (from last_login field)
    print(f"\n{'─'*80}")
    print("RECENT LOGINS:")
    recent_logins = User.objects.exclude(last_login__isnull=True).order_by('-last_login')[:10]
    if recent_logins:
        for user in recent_logins:
            print(f"  {user.username} ({user.email}) - {user.last_login.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("No login records found.")


def view_articles():
    """Display all articles"""
    print_section("ARTICLES")
    
    articles = Article.objects.all()
    if not articles:
        print("No articles found.")
        return
    
    print(f"Total Articles: {articles.count()}")
    print(f"Published: {articles.filter(is_published=True).count()}")
    print(f"Featured: {articles.filter(is_featured=True).count()}")
    
    # Categories
    categories = Category.objects.all()
    print(f"\nTotal Categories: {categories.count()}")
    if categories:
        print("Categories:")
        for cat in categories:
            article_count = cat.articles.count()
            print(f"  - {cat.name} ({article_count} articles)")
    
    print(f"\n{'─'*80}")
    print("ARTICLE DETAILS:")
    for article in articles[:20]:  # Show first 20 articles
        print(f"\n{'─'*80}")
        print(f"ID: {article.id}")
        print(f"Title: {article.title}")
        print(f"Slug: {article.slug}")
        print(f"Author: {article.author.username if article.author else 'N/A'}")
        print(f"Category: {article.category.name if article.category else 'N/A'}")
        print(f"Difficulty: {article.get_difficulty_display()}")
        print(f"Read Time: {article.estimated_read_time} minutes")
        print(f"Views: {article.views_count}")
        print(f"Published: {'Yes' if article.is_published else 'No'}")
        print(f"Featured: {'Yes' if article.is_featured else 'No'}")
        print(f"Created: {article.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Summary: {article.summary[:100] if article.summary else 'N/A'}...")
        
        if article.has_purchase_links():
            print(f"Purchase Links Available:")
            if article.book_title:
                print(f"  Book: {article.book_title}")
            if article.amazon_link:
                print(f"  Amazon: {article.amazon_link[:60]}...")
            if article.flipkart_link:
                print(f"  Flipkart: {article.flipkart_link[:60]}...")
            if article.meesho_link:
                print(f"  Meesho: {article.meesho_link[:60]}...")


def view_user_progress(username=None):
    """Display reading progress for a specific user or all users"""
    print_section("USER READING PROGRESS")
    
    if username:
        try:
            user = User.objects.get(username=username)
            users = [user]
            print(f"Showing progress for user: {username}\n")
        except User.DoesNotExist:
            print(f"User '{username}' not found.")
            return
    else:
        users = User.objects.all()
        print(f"Showing progress for all users\n")
    
    for user in users:
        print(f"\n{'='*80}")
        print(f"USER: {user.username} ({user.email})")
        print(f"{'='*80}")
        
        # Reading Progress
        progress_records = ReadingProgress.objects.filter(user=user)
        print(f"\nReading Progress ({progress_records.count()} articles):")
        if progress_records:
            completed = progress_records.filter(is_completed=True).count()
            in_progress = progress_records.filter(is_completed=False).count()
            print(f"  Completed: {completed}")
            print(f"  In Progress: {in_progress}")
            
            print(f"\n  Article Details:")
            for prog in progress_records[:10]:  # Show first 10
                status = "✓ Completed" if prog.is_completed else "⏳ In Progress"
                print(f"    - {prog.article.title[:50]}")
                print(f"      Progress: {prog.max_scroll_percentage}% | Time: {prog.time_spent}s | {status}")
                print(f"      Last Read: {prog.last_read_at.strftime('%Y-%m-%d %H:%M:%S') if prog.last_read_at else 'N/A'}")
        else:
            print("  No reading progress found.")
        
        # Bookmarks
        bookmarks = Bookmark.objects.filter(user=user)
        print(f"\nBookmarks ({bookmarks.count()}):")
        if bookmarks:
            for bm in bookmarks[:5]:
                print(f"    - {bm.article.title}")
        
        # Reading Streak
        try:
            streak = ReadingStreak.objects.get(user=user)
            print(f"\nReading Streak:")
            print(f"  Current Streak: {streak.current_streak} days")
            print(f"  Longest Streak: {streak.longest_streak} days")
            print(f"  Total Reading Days: {streak.total_reading_days}")
            print(f"  Last Read: {streak.last_read_date if streak.last_read_date else 'N/A'}")
        except ReadingStreak.DoesNotExist:
            print(f"\nReading Streak: Not started")
        
        # Achievements
        achievements = UserAchievement.objects.filter(user=user)
        print(f"\nAchievements ({achievements.count()}):")
        if achievements:
            for ach in achievements:
                print(f"    🏆 {ach.achievement.name} - {ach.earned_at.strftime('%Y-%m-%d')}")
        
        # Notes
        notes = Note.objects.filter(user=user)
        print(f"\nNotes ({notes.count()}):")
        if notes:
            for note in notes[:3]:
                print(f"    - On '{note.article.title}': {note.note[:50]}...")
        
        # Highlights
        highlights = Highlight.objects.filter(user=user)
        print(f"\nHighlights ({highlights.count()}):")
        if highlights:
            for hl in highlights[:3]:
                print(f"    - {hl.text[:50]}... [{hl.color}]")
        
        # Ratings & Reviews
        ratings = Rating.objects.filter(user=user)
        print(f"\nRatings & Reviews ({ratings.count()}):")
        if ratings:
            for rating in ratings[:5]:
                stars = "⭐" * rating.score
                print(f"    - {rating.article.title}: {stars}")
                if rating.review:
                    print(f"      Review: {rating.review[:50]}...")
        
        # Reading Lists
        reading_lists = ReadingList.objects.filter(user=user)
        print(f"\nReading Lists ({reading_lists.count()}):")
        if reading_lists:
            for rl in reading_lists:
                print(f"    - {rl.name} ({rl.articles.count()} articles)")


def main():
    """Main function to display all database records"""
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + " "*20 + "SMART READER DATABASE VIEWER" + " "*31 + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    # Display all records
    view_users()
    view_admins()
    view_signup_login_details()
    view_articles()
    view_user_progress()
    
    # Interactive mode for specific user
    print("\n" + "="*80)
    print("To view a specific user's progress, you can run:")
    print("python view_database_records.py <username>")
    print("="*80)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # View specific user's progress
        username = sys.argv[1]
        view_user_progress(username)
    else:
        # View all records
        main()
