"""
Management command to fix completed articles that have max_scroll_percentage < 100.
This ensures data consistency between is_completed and max_scroll_percentage fields.
"""
from django.core.management.base import BaseCommand
from reader.models import ReadingProgress


class Command(BaseCommand):
    help = 'Fix completed articles to have 100% max_scroll_percentage'

    def handle(self, *args, **options):
        # Find all completed articles with max_scroll_percentage < 100
        articles_to_fix = ReadingProgress.objects.filter(
            is_completed=True,
            max_scroll_percentage__lt=100
        )
        
        count = articles_to_fix.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No articles need fixing. All completed articles already have 100% progress.'))
            return
        
        self.stdout.write(f'Found {count} completed articles with max_scroll_percentage < 100')
        
        # Update them
        updated = articles_to_fix.update(max_scroll_percentage=100)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} articles to 100% progress.'))
