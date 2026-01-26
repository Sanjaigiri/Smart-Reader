"""
Script to check and fix article completion status
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from reader.models import ReadingProgress, Article
from django.contrib.auth.models import User

# Find the article
article = Article.objects.filter(title__icontains='Explore Your Creativity').first()

if not article:
    print("❌ Article 'Explore Your Creativity' not found!")
    print("\nSearching for similar articles...")
    articles = Article.objects.filter(title__icontains='Creativity')
    for art in articles:
        print(f"  - {art.title}")
else:
    print(f"✅ Article found: {article.title}")
    print(f"   ID: {article.id}")
    print(f"   Slug: {article.slug}")
    
    # Find the user
    user = User.objects.filter(username='sanjai').first()
    if not user:
        user = User.objects.first()
    
    if user:
        print(f"\n✅ User: {user.username}")
        
        # Find progress
        progress = ReadingProgress.objects.filter(article=article, user=user).first()
        
        if progress:
            print(f"\n📊 Progress Details:")
            print(f"   Current Scroll: {progress.scroll_percentage}%")
            print(f"   Max Scroll: {progress.max_scroll_percentage}%")
            print(f"   Time Spent: {progress.time_spent}s ({progress.time_spent // 60}m {progress.time_spent % 60}s)")
            print(f"   Completed: {progress.is_completed}")
            
            # Fix completion status if needed
            if progress.max_scroll_percentage >= 90 and not progress.is_completed:
                print(f"\n🔧 Fixing completion status...")
                progress.is_completed = True
                progress.save()
                print(f"✅ Article marked as COMPLETED!")
            elif progress.is_completed:
                print(f"\n✅ Article is already marked as completed!")
            else:
                print(f"\n⚠️  Article not at 90% yet (currently at {progress.max_scroll_percentage}%)")
                print(f"   Need to scroll to at least 90% to mark as complete")
        else:
            print(f"\n❌ No reading progress found for this article")
    else:
        print(f"\n❌ No users found in database")

print("\n" + "="*60)
print("Checking all articles with progress >= 90% but not marked complete...")
print("="*60)

# Fix all articles that should be completed
incomplete_but_finished = ReadingProgress.objects.filter(
    max_scroll_percentage__gte=90,
    is_completed=False
)

if incomplete_but_finished.exists():
    print(f"\nFound {incomplete_but_finished.count()} articles to fix:")
    for prog in incomplete_but_finished:
        print(f"  - {prog.article.title} ({prog.max_scroll_percentage}%) - User: {prog.user.username}")
        prog.is_completed = True
        prog.save()
    print(f"\n✅ Fixed {incomplete_but_finished.count()} articles!")
else:
    print("\n✅ No issues found - all articles properly marked!")
