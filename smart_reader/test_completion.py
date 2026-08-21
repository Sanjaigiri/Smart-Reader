"""
Comprehensive test for article completion functionality
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from reader.models import ReadingProgress, Article
from django.contrib.auth.models import User

print("="*70)
print("ARTICLE COMPLETION TEST - COMPREHENSIVE CHECK")
print("="*70)

# Get user
user = User.objects.filter(username='sanjai').first()
if not user:
    print("❌ User 'sanjai' not found!")
    user = User.objects.first()

if not user:
    print("❌ No users in database!")
    exit()

print(f"\n✅ Testing for user: {user.username}")

# Get all completed articles for the user
completed_articles = ReadingProgress.objects.filter(
    user=user,
    is_completed=True
).select_related('article').order_by('-last_read_at')

print(f"\n📊 COMPLETED ARTICLES ({completed_articles.count()}):")
print("-" * 70)

if completed_articles.exists():
    for i, prog in enumerate(completed_articles, 1):
        print(f"\n{i}. {prog.article.title}")
        print(f"   Max Scroll: {prog.max_scroll_percentage}%")
        print(f"   Current Scroll: {prog.scroll_percentage}%")
        print(f"   Time Spent: {prog.time_spent}s ({prog.time_spent // 60}m {prog.time_spent % 60}s)")
        print(f"   Last Read: {prog.last_read_at}")
        print(f"   Completed: {'✅ YES' if prog.is_completed else '❌ NO'}")
else:
    print("   No completed articles found!")

# Get all in-progress articles
in_progress = ReadingProgress.objects.filter(
    user=user,
    is_completed=False,
    scroll_percentage__gt=0
).select_related('article').order_by('-last_read_at')

print(f"\n\n📖 IN-PROGRESS ARTICLES ({in_progress.count()}):")
print("-" * 70)

if in_progress.exists():
    for i, prog in enumerate(in_progress, 1):
        print(f"\n{i}. {prog.article.title}")
        print(f"   Max Scroll: {prog.max_scroll_percentage}%")
        print(f"   Current Scroll: {prog.scroll_percentage}%")
        print(f"   Time Spent: {prog.time_spent}s")
else:
    print("   No in-progress articles found!")

# Check "Explore Your Creativity" specifically
print(f"\n\n🔍 CHECKING 'Explore Your Creativity' ARTICLE:")
print("-" * 70)

creativity_article = Article.objects.filter(title__icontains='Explore Your Creativity').first()

if creativity_article:
    print(f"\n✅ Article Found:")
    print(f"   Title: {creativity_article.title}")
    print(f"   ID: {creativity_article.id}")
    print(f"   Slug: {creativity_article.slug}")
    
    creativity_progress = ReadingProgress.objects.filter(
        user=user,
        article=creativity_article
    ).first()
    
    if creativity_progress:
        print(f"\n✅ Progress Record Found:")
        print(f"   Max Scroll: {creativity_progress.max_scroll_percentage}%")
        print(f"   Current Scroll: {creativity_progress.scroll_percentage}%")
        print(f"   Completed: {'✅ YES' if creativity_progress.is_completed else '❌ NO'}")
        print(f"   Time Spent: {creativity_progress.time_spent}s")
        print(f"   Last Read: {creativity_progress.last_read_at}")
        
        if creativity_progress.is_completed:
            print(f"\n✅ This article SHOULD appear in the completed list!")
        else:
            print(f"\n⚠️  This article is NOT marked as completed yet.")
            print(f"   Current progress: {creativity_progress.max_scroll_percentage}%")
            print(f"   Needs: 90%+ to be marked as complete")
    else:
        print(f"\n❌ No progress record found for this user!")
else:
    print(f"\n❌ Article 'Explore Your Creativity' not found in database!")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nIf 'Explore Your Creativity' shows as completed above,")
print("it should appear on the My Progress page at: /my-progress/")
print("="*70 + "\n")
