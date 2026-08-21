"""
Smart Reader Database Dashboard
Visual summary of database statistics
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Count, Sum, Avg
from reader.models import (
    UserProfile, Article, Category, ReadingProgress,
    Bookmark, Note, Highlight, Rating, ReadingStreak,
    UserAchievement, OTPVerification
)


def print_dashboard():
    """Display a visual dashboard of database statistics"""
    
    # Header
    print("\n" + "█"*100)
    print("█" + " "*98 + "█")
    print("█" + " "*30 + "SMART READER DATABASE DASHBOARD" + " "*37 + "█")
    print("█" + " "*98 + "█")
    print("█"*100)
    
    # User Statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    admin_users = User.objects.filter(is_superuser=True).count() + User.objects.filter(is_staff=True).count()
    verified_users = UserProfile.objects.filter(is_email_verified=True).count()
    
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*40 + "👥 USER STATISTICS" + " "*40 + "│")
    print("├" + "─"*98 + "┤")
    print(f"│  Total Users: {total_users:<10}  Active: {active_users:<10}  Admins: {admin_users:<10}  Email Verified: {verified_users:<10}  │")
    print("└" + "─"*98 + "┘")
    
    # Top Users by Activity
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*35 + "🏆 TOP ACTIVE USERS" + " "*43 + "│")
    print("├" + "─"*98 + "┤")
    
    # Get users with reading progress
    users_with_progress = User.objects.annotate(
        article_count=Count('reading_progress'),
        total_time=Sum('reading_progress__time_spent')
    ).filter(article_count__gt=0).order_by('-article_count')[:5]
    
    if users_with_progress:
        print("│ " + f"{'Rank':<6}{'Username':<20}{'Articles':<12}{'Time':<15}{'Completed':<15}" + " "*30 + "│")
        print("├" + "─"*98 + "┤")
        for i, user in enumerate(users_with_progress, 1):
            completed = ReadingProgress.objects.filter(user=user, is_completed=True).count()
            time_h = (user.total_time or 0) // 3600
            time_m = ((user.total_time or 0) % 3600) // 60
            time_str = f"{time_h}h {time_m}m"
            print(f"│ {i:<6}{user.username[:19]:<20}{user.article_count:<12}{time_str:<15}{completed:<15}" + " "*30 + "│")
    else:
        print("│" + " "*40 + "No reading activity yet" + " "*35 + "│")
    
    print("└" + "─"*98 + "┘")
    
    # Article Statistics
    total_articles = Article.objects.count()
    published_articles = Article.objects.filter(is_published=True).count()
    featured_articles = Article.objects.filter(is_featured=True).count()
    total_categories = Category.objects.count()
    
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*37 + "📚 ARTICLE STATISTICS" + " "*40 + "│")
    print("├" + "─"*98 + "┤")
    print(f"│  Total: {total_articles:<12}  Published: {published_articles:<12}  Featured: {featured_articles:<12}  Categories: {total_categories:<12}  │")
    print("└" + "─"*98 + "┘")
    
    # Top Categories
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*35 + "📊 TOP 10 CATEGORIES" + " "*42 + "│")
    print("├" + "─"*98 + "┤")
    
    top_categories = Category.objects.annotate(
        article_count=Count('articles')
    ).order_by('-article_count')[:10]
    
    if top_categories:
        print("│ " + f"{'Rank':<6}{'Category':<40}{'Articles':<20}" + " "*32 + "│")
        print("├" + "─"*98 + "┤")
        for i, cat in enumerate(top_categories, 1):
            if cat.article_count > 0:
                print(f"│ {i:<6}{cat.name[:39]:<40}{cat.article_count:<20}" + " "*32 + "│")
    
    print("└" + "─"*98 + "┘")
    
    # Reading Engagement
    total_progress = ReadingProgress.objects.count()
    completed_articles = ReadingProgress.objects.filter(is_completed=True).count()
    total_bookmarks = Bookmark.objects.count()
    total_notes = Note.objects.count()
    total_highlights = Highlight.objects.count()
    
    completion_rate = (completed_articles / total_progress * 100) if total_progress > 0 else 0
    
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*35 + "📖 READING ENGAGEMENT" + " "*41 + "│")
    print("├" + "─"*98 + "┤")
    print(f"│  Articles Started: {total_progress:<10}  Completed: {completed_articles:<10}  Completion Rate: {completion_rate:.1f}%" + " "*30 + "│")
    print(f"│  Bookmarks: {total_bookmarks:<10}  Notes: {total_notes:<10}  Highlights: {total_highlights:<10}" + " "*40 + "│")
    print("└" + "─"*98 + "┘")
    
    # Ratings
    total_ratings = Rating.objects.count()
    if total_ratings > 0:
        avg_rating = Rating.objects.aggregate(Avg('score'))['score__avg']
        print("\n┌" + "─"*98 + "┐")
        print("│" + " "*38 + "⭐ RATING STATISTICS" + " "*40 + "│")
        print("├" + "─"*98 + "┤")
        print(f"│  Total Ratings: {total_ratings:<10}  Average Rating: {avg_rating:.2f}⭐" + " "*50 + "│")
        print("└" + "─"*98 + "┘")
    
    # Reading Streaks
    streaks = ReadingStreak.objects.all()
    if streaks:
        max_current_streak = max([s.current_streak for s in streaks])
        max_longest_streak = max([s.longest_streak for s in streaks])
        total_reading_days = sum([s.total_reading_days for s in streaks])
        
        print("\n┌" + "─"*98 + "┐")
        print("│" + " "*38 + "🔥 READING STREAKS" + " "*42 + "│")
        print("├" + "─"*98 + "┤")
        print(f"│  Best Current Streak: {max_current_streak} days  │  Best All-Time: {max_longest_streak} days  │  Total Reading Days: {total_reading_days}" + " "*20 + "│")
        print("└" + "─"*98 + "┘")
    
    # Achievements
    total_achievements_earned = UserAchievement.objects.count()
    users_with_achievements = User.objects.annotate(
        achievement_count=Count('achievements')
    ).filter(achievement_count__gt=0).count()
    
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*38 + "🏆 ACHIEVEMENTS" + " "*44 + "│")
    print("├" + "─"*98 + "┤")
    print(f"│  Total Earned: {total_achievements_earned:<10}  Users with Achievements: {users_with_achievements:<10}" + " "*40 + "│")
    print("└" + "─"*98 + "┘")
    
    # OTP Verification
    total_otps = OTPVerification.objects.count()
    verified_otps = OTPVerification.objects.filter(is_verified=True).count()
    
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*35 + "📧 EMAIL VERIFICATION" + " "*41 + "│")
    print("├" + "─"*98 + "┤")
    print(f"│  Total OTP Sent: {total_otps:<10}  Verified: {verified_otps:<10}  Pending: {total_otps - verified_otps:<10}" + " "*40 + "│")
    print("└" + "─"*98 + "┘")
    
    # Recent Activity Summary
    recent_logins = User.objects.exclude(last_login__isnull=True).order_by('-last_login')[:5]
    
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*36 + "🕐 RECENT ACTIVITY" + " "*43 + "│")
    print("├" + "─"*98 + "┤")
    
    if recent_logins:
        print("│ " + f"{'Username':<25}{'Last Login':<30}" + " "*43 + "│")
        print("├" + "─"*98 + "┤")
        for user in recent_logins:
            login_time = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'
            print(f"│ {user.username[:24]:<25}{login_time:<30}" + " "*43 + "│")
    
    print("└" + "─"*98 + "┘")
    
    # Overall Summary
    print("\n┌" + "─"*98 + "┐")
    print("│" + " "*38 + "📊 QUICK SUMMARY" + " "*44 + "│")
    print("├" + "─"*98 + "┤")
    print(f"│  • {total_users} registered users ({active_users} active, {admin_users} admins)" + " "*50 + "│")
    print(f"│  • {total_articles:,} total articles across {total_categories} categories" + " "*45 + "│")
    print(f"│  • {total_progress} articles started by users, {completed_articles} completed ({completion_rate:.1f}%)" + " "*30 + "│")
    print(f"│  • {total_bookmarks} bookmarks, {total_notes} notes, {total_highlights} highlights created" + " "*35 + "│")
    print(f"│  • {total_achievements_earned} achievements earned by {users_with_achievements} users" + " "*45 + "│")
    print("└" + "─"*98 + "┘")
    
    # Footer
    print("\n" + "█"*100)
    print("█" + " "*20 + "Database: smart_reader | Location: db.sqlite3" + " "*34 + "█")
    print("█"*100 + "\n")
    
    # Quick Actions
    print("📌 Quick Actions:")
    print("  • View all users: python view_database_records.py")
    print("  • Check user progress: python check_user_progress.py <username>")
    print("  • Interactive mode: python query_database.py")
    print("  • View this dashboard: python dashboard.py")
    print()


if __name__ == "__main__":
    print_dashboard()
