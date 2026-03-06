"""
Quick User Progress Checker
Usage: python check_user_progress.py <username>
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
    UserProfile, ReadingProgress, Bookmark, ReadingStreak,
    UserAchievement, Note, Highlight, Rating, ReadingList,
    Article
)


def get_user_statistics(user):
    """Get comprehensive statistics for a user"""
    stats = {}
    
    # Reading Progress Statistics
    progress_records = ReadingProgress.objects.filter(user=user)
    stats['total_articles_started'] = progress_records.count()
    stats['completed_articles'] = progress_records.filter(is_completed=True).count()
    stats['in_progress_articles'] = progress_records.filter(is_completed=False).count()
    
    # Calculate total time spent
    total_seconds = sum(p.time_spent for p in progress_records)
    stats['total_hours'] = total_seconds // 3600
    stats['total_minutes'] = (total_seconds % 3600) // 60
    stats['total_seconds'] = total_seconds
    
    # Average progress
    if progress_records:
        stats['average_progress'] = sum(p.max_scroll_percentage for p in progress_records) / progress_records.count()
    else:
        stats['average_progress'] = 0
    
    # Bookmarks
    stats['bookmarks_count'] = Bookmark.objects.filter(user=user).count()
    
    # Notes & Highlights
    stats['notes_count'] = Note.objects.filter(user=user).count()
    stats['highlights_count'] = Highlight.objects.filter(user=user).count()
    
    # Ratings
    ratings = Rating.objects.filter(user=user)
    stats['ratings_count'] = ratings.count()
    if ratings:
        stats['average_rating_given'] = sum(r.score for r in ratings) / ratings.count()
    else:
        stats['average_rating_given'] = 0
    
    # Achievements
    stats['achievements_count'] = UserAchievement.objects.filter(user=user).count()
    
    # Reading Lists
    stats['reading_lists_count'] = ReadingList.objects.filter(user=user).count()
    
    # Streak
    try:
        streak = ReadingStreak.objects.get(user=user)
        stats['current_streak'] = streak.current_streak
        stats['longest_streak'] = streak.longest_streak
        stats['total_reading_days'] = streak.total_reading_days
    except:
        stats['current_streak'] = 0
        stats['longest_streak'] = 0
        stats['total_reading_days'] = 0
    
    return stats


def display_user_progress(username):
    """Display comprehensive progress for a user"""
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"\n❌ User '{username}' not found in database.")
        print("\nAvailable users:")
        for u in User.objects.all()[:10]:
            print(f"  - {u.username}")
        return
    
    # Header
    print("\n" + "="*100)
    print(f"{'USER PROGRESS REPORT':^100}")
    print("="*100)
    
    # User Info
    print(f"\n{'BASIC INFORMATION':^100}")
    print("-"*100)
    print(f"{'Username:':<30} {user.username}")
    print(f"{'Email:':<30} {user.email}")
    print(f"{'Full Name:':<30} {user.first_name} {user.last_name}")
    print(f"{'User ID:':<30} {user.id}")
    print(f"{'Account Type:':<30} {'Admin' if (user.is_superuser or user.is_staff) else 'Regular User'}")
    print(f"{'Status:':<30} {'✓ Active' if user.is_active else '✗ Inactive'}")
    print(f"{'Date Joined:':<30} {user.date_joined.strftime('%B %d, %Y at %H:%M:%S')}")
    print(f"{'Last Login:':<30} {user.last_login.strftime('%B %d, %Y at %H:%M:%S') if user.last_login else 'Never'}")
    
    # Profile
    try:
        profile = user.profile
        print(f"\n{'PROFILE SETTINGS':^100}")
        print("-"*100)
        print(f"{'Bio:':<30} {profile.bio if profile.bio else 'Not set'}")
        print(f"{'Reading Goal:':<30} {profile.reading_goal} articles per week")
        print(f"{'Email Verified:':<30} {'✓ Yes' if profile.is_email_verified else '✗ No'}")
        print(f"{'Preferred Language:':<30} {profile.get_language_display()}")
        print(f"{'Theme Preference:':<30} {profile.get_theme_display()}")
        print(f"{'Font Size:':<30} {profile.preferred_font_size}px")
    except:
        print(f"\n{'PROFILE SETTINGS':^100}")
        print("-"*100)
        print("Profile not created yet")
    
    # Statistics
    stats = get_user_statistics(user)
    print(f"\n{'READING STATISTICS':^100}")
    print("-"*100)
    print(f"{'Total Articles Started:':<30} {stats['total_articles_started']}")
    print(f"{'Completed:':<30} {stats['completed_articles']} ({(stats['completed_articles']/stats['total_articles_started']*100) if stats['total_articles_started'] > 0 else 0:.1f}%)")
    print(f"{'In Progress:':<30} {stats['in_progress_articles']}")
    print(f"{'Average Progress:':<30} {stats['average_progress']:.1f}%")
    print(f"{'Total Reading Time:':<30} {stats['total_hours']}h {stats['total_minutes']}m")
    print(f"{'Bookmarks:':<30} {stats['bookmarks_count']}")
    print(f"{'Notes Created:':<30} {stats['notes_count']}")
    print(f"{'Text Highlights:':<30} {stats['highlights_count']}")
    print(f"{'Ratings Given:':<30} {stats['ratings_count']} (Avg: {stats['average_rating_given']:.1f}⭐)")
    print(f"{'Reading Lists:':<30} {stats['reading_lists_count']}")
    print(f"{'Achievements Earned:':<30} {stats['achievements_count']}")
    
    # Streak
    print(f"\n{'READING STREAK':^100}")
    print("-"*100)
    print(f"{'Current Streak:':<30} 🔥 {stats['current_streak']} days")
    print(f"{'Longest Streak:':<30} 🏆 {stats['longest_streak']} days")
    print(f"{'Total Reading Days:':<30} 📅 {stats['total_reading_days']} days")
    
    # Recent Activity
    progress_records = ReadingProgress.objects.filter(user=user).order_by('-last_read_at')[:10]
    if progress_records:
        print(f"\n{'RECENT READING ACTIVITY (Last 10)':^100}")
        print("-"*100)
        print(f"{'Article Title':<65} {'Progress':<12} {'Status':<15}")
        print("-"*100)
        for prog in progress_records:
            title = prog.article.title[:62] + "..." if len(prog.article.title) > 62 else prog.article.title
            progress = f"{prog.max_scroll_percentage}%"
            status = "✓ Completed" if prog.is_completed else "⏳ Reading"
            print(f"{title:<65} {progress:<12} {status:<15}")
    
    # Completed Articles
    completed = ReadingProgress.objects.filter(user=user, is_completed=True).order_by('-last_read_at')[:10]
    if completed:
        print(f"\n{'COMPLETED ARTICLES (Last 10)':^100}")
        print("-"*100)
        for i, prog in enumerate(completed, 1):
            print(f"{i}. {prog.article.title}")
            print(f"   Category: {prog.article.category.name if prog.article.category else 'N/A'} | "
                  f"Difficulty: {prog.get_difficulty_display() if hasattr(prog, 'get_difficulty_display') else prog.article.get_difficulty_display()} | "
                  f"Time: {prog.time_spent}s | "
                  f"Completed: {prog.last_read_at.strftime('%Y-%m-%d')}")
    
    # In Progress Articles
    in_progress = ReadingProgress.objects.filter(user=user, is_completed=False).order_by('-last_read_at')[:10]
    if in_progress:
        print(f"\n{'IN PROGRESS ARTICLES':^100}")
        print("-"*100)
        for i, prog in enumerate(in_progress, 1):
            print(f"{i}. {prog.article.title}")
            print(f"   Progress: {prog.max_scroll_percentage}% | "
                  f"Time Spent: {prog.time_spent}s | "
                  f"Last Read: {prog.last_read_at.strftime('%Y-%m-%d %H:%M') if prog.last_read_at else 'N/A'}")
    
    # Bookmarks
    bookmarks = Bookmark.objects.filter(user=user).order_by('-created_at')[:10]
    if bookmarks:
        print(f"\n{'BOOKMARKED ARTICLES':^100}")
        print("-"*100)
        for i, bm in enumerate(bookmarks, 1):
            print(f"{i}. {bm.article.title}")
            print(f"   Added: {bm.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Achievements
    achievements = UserAchievement.objects.filter(user=user).order_by('-earned_at')
    if achievements:
        print(f"\n{'ACHIEVEMENTS EARNED':^100}")
        print("-"*100)
        for ach in achievements:
            print(f"🏆 {ach.achievement.name}")
            print(f"   {ach.achievement.description}")
            print(f"   Earned on: {ach.earned_at.strftime('%B %d, %Y')}")
            print()
    
    # Notes
    notes = Note.objects.filter(user=user).order_by('-created_at')[:5]
    if notes:
        print(f"\n{'RECENT NOTES':^100}")
        print("-"*100)
        for i, note in enumerate(notes, 1):
            print(f"{i}. Article: {note.article.title}")
            print(f"   Note: {note.note[:200]}...")
            print(f"   Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
            print()
    
    # Reading Lists
    reading_lists = ReadingList.objects.filter(user=user)
    if reading_lists:
        print(f"\n{'READING LISTS':^100}")
        print("-"*100)
        for rl in reading_lists:
            visibility = "🌐 Public" if rl.is_public else "🔒 Private"
            print(f"📚 {rl.name} ({rl.articles.count()} articles) - {visibility}")
            if rl.description:
                print(f"   {rl.description}")
            print(f"   Created: {rl.created_at.strftime('%Y-%m-%d')}")
            print()
    
    print("="*100)
    print(f"{'END OF REPORT':^100}")
    print("="*100 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\nUsage: python check_user_progress.py <username>")
        print("\nExample: python check_user_progress.py sanjai")
        print("\nAvailable users:")
        for user in User.objects.all():
            admin_tag = " (Admin)" if (user.is_superuser or user.is_staff) else ""
            print(f"  - {user.username}{admin_tag}")
    else:
        username = sys.argv[1]
        display_user_progress(username)
