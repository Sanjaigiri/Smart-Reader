"""
Management command to balance articles across categories (keep only 1000 per category)
Usage: python manage.py balance_articles
"""

from django.core.management.base import BaseCommand
from reader.models import Article, Category


class Command(BaseCommand):
    help = 'Balance articles to have exactly 1000 per category'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=1000,
            help='Number of articles to keep per category (default: 1000)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS(f'\n🔧 Balancing Articles to {limit} per category...\n'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No articles will be deleted\n'))
        
        categories = Category.objects.all()
        total_deleted = 0
        
        for category in categories:
            articles = Article.objects.filter(category=category).order_by('-created_at')
            count = articles.count()
            
            if count > limit:
                excess = count - limit
                # Keep the most recent 'limit' articles, delete the rest
                articles_to_delete = articles[limit:]
                
                self.stdout.write(f'📊 {category.name}:')
                self.stdout.write(f'   Current: {count:,} articles')
                self.stdout.write(f'   Excess: {excess:,} articles')
                
                if not dry_run:
                    deleted_count = articles_to_delete.delete()[0]
                    total_deleted += deleted_count
                    remaining = Article.objects.filter(category=category).count()
                    self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted {deleted_count:,} articles, kept {remaining:,}'))
                else:
                    self.stdout.write(self.style.WARNING(f'   ⚠️  Would delete {excess:,} articles'))
            else:
                self.stdout.write(f'✓ {category.name}: {count:,} articles (OK)')
        
        if not dry_run:
            self.stdout.write(self.style.SUCCESS(f'\n🎉 Balancing Complete!'))
            self.stdout.write(f'   Total articles deleted: {total_deleted:,}')
            self.stdout.write(f'   Total articles remaining: {Article.objects.count():,}')
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  DRY RUN - Run without --dry-run to actually delete'))
        
        # Show final distribution
        self.stdout.write(self.style.SUCCESS('\n📊 Final Distribution:'))
        for category in Category.objects.all():
            count = Article.objects.filter(category=category).count()
            status = '✅' if count == limit else ('⚠️' if count < limit else '❌')
            self.stdout.write(f'   {status} {category.name}: {count:,} articles')
        
        total = Article.objects.count()
        expected = Category.objects.count() * limit
        self.stdout.write(f'\n   Total: {total:,} articles')
        self.stdout.write(f'   Expected: {expected:,} articles')
