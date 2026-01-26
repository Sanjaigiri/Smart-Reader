"""
Display article distribution across all categories
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from reader.models import Article, Category

def main():
    total = Article.objects.count()
    cats = Category.objects.all().order_by('name')
    
    print("\n" + "="*70)
    print("📊 ARTICLE DISTRIBUTION ACROSS ALL 61 CATEGORIES")
    print("="*70)
    print()
    
    for i, cat in enumerate(cats, 1):
        count = Article.objects.filter(category=cat).count()
        bar = '█' * min(int(count/100), 50) if count > 0 else ''
        print(f"{i:2}. {cat.name:.<40} {count:>6,} {bar}")
    
    print()
    print("="*70)
    print(f"TOTAL ARTICLES:        {total:>10,}")
    print(f"TOTAL CATEGORIES:      {cats.count():>10}")
    print(f"AVERAGE PER CATEGORY:  {total//cats.count() if cats.count() > 0 else 0:>10,}")
    print(f"TARGET:                   100,000+")
    print(f"REMAINING:             {100000-total:>10,}")
    print(f"PROGRESS:              {(total/100000*100):>9.1f}%")
    print("="*70)
    print()

if __name__ == "__main__":
    main()
