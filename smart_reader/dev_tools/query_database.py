"""
Interactive Database Query Tool
Query specific user progress and details
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
    UserAchievement, Note, Highlight, Rating, ReadingList
)


def search_user():
    """Search for users by username or email"""
    print("\n" + "="*80)
    print("SEARCH USERS")
    print("="*80)
    
    query = input("\nEnter username or email to search: ").strip()
    
    if not query:
        print("No search query provided.")
        return
    
    users = User.objects.filter(username__icontains=query) | User.objects.filter(email__icontains=query)
    
    if not users:
        print(f"\nNo users found matching '{query}'")
        return
    
    print(f"\n{users.count()} user(s) found:")
    print("-" * 80)
    
    for i, user in enumerate(users, 1):
        print(f"\n{i}. Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Full Name: {user.first_name} {user.last_name}")
        print(f"   Is Admin: {'Yes' if user.is_superuser or user.is_staff else 'No'}")
        print(f"   Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("-" * 80)
    choice = input("\nEnter number to view detailed progress (or press Enter to skip): ").strip()
    
    if choice.isdigit() and 1 <= int(choice) <= users.count():
        selected_user = list(users)[int(choice) - 1]
        show_detailed_progress(selected_user)


def show_detailed_progress(user):
    """Show detailed progress for a specific user"""
    print("\n" + "="*80)
    print(f"DETAILED PROGRESS FOR: {user.username}")
    print("="*80)
    
    # Basic Info
    print(f"\nUser ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Full Name: {user.first_name} {user.last_name}")
    print(f"Is Admin: {'Yes' if user.is_superuser or user.is_staff else 'No'}")
    print(f"Is Active: {'Yes' if user.is_active else 'No'}")
    print(f"Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Last Login: {user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never'}")
    
    # Profile
    try:
        profile = user.profile
        print(f"\n{'─'*80}")
        print("PROFILE INFORMATION:")
        print(f"  Bio: {profile.bio if profile.bio else 'Not set'}")
        print(f"  Reading Goal: {profile.reading_goal} articles/week")
        print(f"  Email Verified: {'✓ Yes' if profile.is_email_verified else '✗ No'}")
        print(f"  Language: {profile.get_language_display()}")
        print(f"  Theme: {profile.get_theme_display()}")
        print(f"  Font Size: {profile.preferred_font_size}px")
    except:
        print(f"\nProfile: Not created")
    
    # Reading Progress
    progress_records = ReadingProgress.objects.filter(user=user)
    print(f"\n{'─'*80}")
    print(f"READING PROGRESS: {progress_records.count()} articles")
    
    if progress_records:
        completed = progress_records.filter(is_completed=True)
        in_progress = progress_records.filter(is_completed=False)
        
        print(f"  ✓ Completed: {completed.count()}")
        print(f"  ⏳ In Progress: {in_progress.count()}")
        
        total_time = sum(p.time_spent for p in progress_records)
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        print(f"  ⏱ Total Time Spent: {hours}h {minutes}m")
        
        if completed:
            print(f"\n  Completed Articles:")
            for prog in completed[:10]:
                print(f"    ✓ {prog.article.title[:60]}")
                print(f"      Progress: {prog.max_scroll_percentage}% | Time: {prog.time_spent}s")
                print(f"      Completed: {prog.last_read_at.strftime('%Y-%m-%d %H:%M') if prog.last_read_at else 'N/A'}")
        
        if in_progress:
            print(f"\n  In Progress Articles:")
            for prog in in_progress[:10]:
                print(f"    ⏳ {prog.article.title[:60]}")
                print(f"      Progress: {prog.max_scroll_percentage}% | Time: {prog.time_spent}s")
                print(f"      Last Read: {prog.last_read_at.strftime('%Y-%m-%d %H:%M') if prog.last_read_at else 'N/A'}")
    else:
        print("  No reading activity yet")
    
    # Reading Streak
    print(f"\n{'─'*80}")
    print("READING STREAK:")
    try:
        streak = ReadingStreak.objects.get(user=user)
        print(f"  🔥 Current Streak: {streak.current_streak} days")
        print(f"  🏆 Longest Streak: {streak.longest_streak} days")
        print(f"  📅 Total Reading Days: {streak.total_reading_days}")
        print(f"  📖 Last Read: {streak.last_read_date if streak.last_read_date else 'N/A'}")
    except:
        print("  No streak data available")
    
    # Bookmarks
    bookmarks = Bookmark.objects.filter(user=user)
    print(f"\n{'─'*80}")
    print(f"BOOKMARKS: {bookmarks.count()}")
    if bookmarks:
        for bm in bookmarks[:10]:
            print(f"  📌 {bm.article.title}")
            print(f"     Added: {bm.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Achievements
    achievements = UserAchievement.objects.filter(user=user)
    print(f"\n{'─'*80}")
    print(f"ACHIEVEMENTS: {achievements.count()}")
    if achievements:
        for ach in achievements:
            print(f"  🏆 {ach.achievement.name}")
            print(f"     {ach.achievement.description}")
            print(f"     Earned: {ach.earned_at.strftime('%Y-%m-%d')}")
    
    # Notes
    notes = Note.objects.filter(user=user)
    print(f"\n{'─'*80}")
    print(f"NOTES: {notes.count()}")
    if notes:
        for note in notes[:5]:
            print(f"  📝 On '{note.article.title[:50]}'")
            print(f"     {note.note[:100]}...")
            print(f"     Created: {note.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Highlights
    highlights = Highlight.objects.filter(user=user)
    print(f"\n{'─'*80}")
    print(f"HIGHLIGHTS: {highlights.count()}")
    if highlights:
        for hl in highlights[:5]:
            print(f"  🖍 [{hl.color}] {hl.text[:80]}...")
            print(f"     Article: {hl.article.title[:50]}")
    
    # Ratings & Reviews
    ratings = Rating.objects.filter(user=user)
    print(f"\n{'─'*80}")
    print(f"RATINGS & REVIEWS: {ratings.count()}")
    if ratings:
        avg_rating = sum(r.score for r in ratings) / ratings.count()
        print(f"  Average Rating Given: {avg_rating:.1f} ⭐")
        print(f"\n  Recent Ratings:")
        for rating in ratings[:5]:
            stars = "⭐" * rating.score
            print(f"    {stars} {rating.article.title[:50]}")
            if rating.review:
                print(f"       Review: {rating.review[:80]}...")
    
    # Reading Lists
    reading_lists = ReadingList.objects.filter(user=user)
    print(f"\n{'─'*80}")
    print(f"READING LISTS: {reading_lists.count()}")
    if reading_lists:
        for rl in reading_lists:
            visibility = "🌐 Public" if rl.is_public else "🔒 Private"
            print(f"  📚 {rl.name} ({rl.articles.count()} articles) - {visibility}")
            if rl.description:
                print(f"     {rl.description[:80]}")


def list_all_users():
    """List all registered users"""
    print("\n" + "="*80)
    print("ALL REGISTERED USERS")
    print("="*80)
    
    users = User.objects.all().order_by('-date_joined')
    
    print(f"\nTotal Users: {users.count()}")
    print(f"Active Users: {users.filter(is_active=True).count()}")
    print(f"Admin Users: {User.objects.filter(is_superuser=True).count() + User.objects.filter(is_staff=True).count()}")
    print(f"Regular Users: {users.filter(is_superuser=False, is_staff=False).count()}")
    
    print("\n" + "-"*80)
    print(f"{'ID':<6} {'Username':<20} {'Email':<30} {'Admin':<8} {'Joined':<12}")
    print("-"*80)
    
    for user in users:
        admin_status = "Yes" if (user.is_superuser or user.is_staff) else "No"
        print(f"{user.id:<6} {user.username[:20]:<20} {user.email[:30]:<30} {admin_status:<8} {user.date_joined.strftime('%Y-%m-%d'):<12}")


def main_menu():
    """Main interactive menu"""
    while True:
        print("\n" + "█"*80)
        print("█" + " "*78 + "█")
        print("█" + " "*20 + "SMART READER DATABASE QUERY TOOL" + " "*27 + "█")
        print("█" + " "*78 + "█")
        print("█"*80)
        
        print("\nOptions:")
        print("  1. List all users")
        print("  2. Search for a user")
        print("  3. View specific user progress")
        print("  4. View all database records")
        print("  5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            list_all_users()
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            search_user()
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            username = input("\nEnter username: ").strip()
            try:
                user = User.objects.get(username=username)
                show_detailed_progress(user)
                input("\nPress Enter to continue...")
            except User.DoesNotExist:
                print(f"\nUser '{username}' not found.")
                input("\nPress Enter to continue...")
        
        elif choice == '4':
            print("\nLoading all database records...")
            os.system('python view_database_records.py')
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            print("\nExiting... Goodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main_menu()
