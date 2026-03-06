"""
Script to generate sample analytics data for testing
Run this to populate the database with sample visits and activity
"""
import os
import django
import sys
from datetime import datetime, timedelta
import random

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.contrib.auth.models import User
from reader.models import SiteVisit, ArticleViewLog, Article, ReadingProgress
from django.utils import timezone


def generate_sample_data():
    """Generate sample analytics data for the last 30 days"""
    
    print("🎯 Generating sample analytics data...")
    
    # Get all users
    users = list(User.objects.all())
    if not users:
        print("❌ No users found. Please create some users first.")
        return
    
    # Get all articles
    articles = list(Article.objects.all())
    if not articles:
        print("❌ No articles found. Please create some articles first.")
        return
    
    today = timezone.now()
    
    # Generate site visits for the last 30 days
    print("📊 Generating site visits...")
    pages = ['/', '/articles/', '/dashboard/', '/search/']
    
    for day in range(30):
        visit_date = (today - timedelta(days=day)).date()
        
        # Random number of visits per day (10-50)
        num_visits = random.randint(10, 50)
        
        for _ in range(num_visits):
            user = random.choice(users) if random.random() > 0.3 else None
            SiteVisit.objects.create(
                user=user,
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                user_agent="Mozilla/5.0 (Test Browser)",
                visit_date=visit_date,
                visit_time=timezone.make_aware(
                    datetime.combine(visit_date, datetime.min.time()) + 
                    timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
                ),
                page_visited=random.choice(pages)
            )
    
    print(f"✅ Generated site visits for the last 30 days")
    
    # Generate article views
    print("📚 Generating article views...")
    for day in range(30):
        view_date = (today - timedelta(days=day))
        
        # Random number of article views per day (5-30)
        num_views = random.randint(5, 30)
        
        for _ in range(num_views):
            user = random.choice(users) if random.random() > 0.2 else None
            article = random.choice(articles)
            ArticleViewLog.objects.create(
                article=article,
                user=user,
                ip_address=f"192.168.1.{random.randint(1, 255)}",
                viewed_at=view_date - timedelta(hours=random.randint(0, 23)),
                time_spent=random.randint(30, 600)  # 30 seconds to 10 minutes
            )
            
            # Update article views count
            article.views_count += 1
            article.save()
    
    print(f"✅ Generated article views for the last 30 days")
    
    # Generate reading progress
    print("📖 Generating reading progress...")
    for user in users:
        # Each user has read 3-10 articles
        num_articles = random.randint(3, min(10, len(articles)))
        user_articles = random.sample(articles, num_articles)
        
        for article in user_articles:
            # Some articles are completed
            is_completed = random.random() > 0.5
            progress = 100 if is_completed else random.randint(10, 90)
            
            ReadingProgress.objects.get_or_create(
                user=user,
                article=article,
                defaults={
                    'scroll_percentage': progress,
                    'max_scroll_percentage': progress,
                    'is_completed': is_completed,
                    'last_read_at': timezone.now() - timedelta(days=random.randint(0, 15)),
                    'time_spent': random.randint(60, 1800)  # 1 to 30 minutes
                }
            )
    
    print(f"✅ Generated reading progress")
    
    # Summary
    total_visits = SiteVisit.objects.count()
    total_views = ArticleViewLog.objects.count()
    total_progress = ReadingProgress.objects.count()
    
    print("\n" + "="*50)
    print("📈 Sample Data Generation Complete!")
    print("="*50)
    print(f"✅ Total Site Visits: {total_visits}")
    print(f"✅ Total Article Views: {total_views}")
    print(f"✅ Total Reading Progress Records: {total_progress}")
    print("\n🎉 Your analytics dashboard should now show meaningful data!")
    print("👉 Visit the admin analytics page to see the results")
    print("="*50)


if __name__ == "__main__":
    try:
        generate_sample_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
