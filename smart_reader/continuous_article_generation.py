"""
Continuous article generation script
This runs independently and generates articles until reaching 100,000+
Run with: python continuous_article_generation.py
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from reader.models import Article, Category
from django.core.management import call_command

def main():
    print("=" * 70)
    print("🚀 CONTINUOUS ARTICLE GENERATION SYSTEM")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    target = 100000
    batch_size = 1000
    
    while True:
        try:
            current_count = Article.objects.count()
            remaining = target - current_count
            
            if current_count >= target:
                print(f"\n✅ TARGET REACHED!")
                print(f"Total Articles: {current_count:,}")
                print(f"Target: {target:,}")
                print(f"Success! 🎉")
                break
            
            print(f"\n📊 Current Status:")
            print(f"   Total Articles: {current_count:,}")
            print(f"   Target: {target:,}")
            print(f"   Remaining: {remaining:,}")
            print(f"   Progress: {(current_count/target*100):.1f}%")
            print()
            
            # Generate batch
            batch = min(batch_size, remaining)
            print(f"🔄 Generating batch of {batch:,} articles...")
            
            call_command('generate_massive_articles', total=target, batch=batch)
            
            # Brief pause between batches
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Generation stopped by user")
            current = Article.objects.count()
            print(f"Current total: {current:,} articles")
            print(f"Remaining to 100k: {target - current:,} articles")
            break
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
            continue
    
    print("\n" + "=" * 70)
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

if __name__ == "__main__":
    main()
