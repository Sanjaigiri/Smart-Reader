"""
Management command to delete ALL articles from the database
Usage: python manage.py delete_all_articles
"""

from django.core.management.base import BaseCommand
from reader.models import Article, ReadingProgress, Bookmark, Highlight, Note


class Command(BaseCommand):
    help = 'Delete ALL articles and related data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion without prompt'
        )

    def handle(self, *args, **options):
        confirm = options.get('confirm', False)
        
        # Count current articles
        article_count = Article.objects.count()
        progress_count = ReadingProgress.objects.count()
        bookmark_count = Bookmark.objects.count()
        highlight_count = Highlight.objects.count()
        note_count = Note.objects.count()
        
        self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will delete ALL data!'))
        self.stdout.write(f'   Articles: {article_count:,}')
        self.stdout.write(f'   Reading Progress: {progress_count:,}')
        self.stdout.write(f'   Bookmarks: {bookmark_count:,}')
        self.stdout.write(f'   Highlights: {highlight_count:,}')
        self.stdout.write(f'   Notes: {note_count:,}')
        
        if not confirm:
            response = input('\nType "DELETE ALL" to confirm: ')
            if response != 'DELETE ALL':
                self.stdout.write(self.style.ERROR('\n❌ Deletion cancelled.'))
                return
        
        self.stdout.write(self.style.WARNING('\n🗑️  Deleting all data...'))
        
        # Delete in order (related data first)
        self.stdout.write('   Deleting reading progress...')
        ReadingProgress.objects.all().delete()
        
        self.stdout.write('   Deleting bookmarks...')
        Bookmark.objects.all().delete()
        
        self.stdout.write('   Deleting highlights...')
        Highlight.objects.all().delete()
        
        self.stdout.write('   Deleting notes...')
        Note.objects.all().delete()
        
        self.stdout.write('   Deleting articles...')
        Article.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS('\n✅ ALL articles and related data deleted!'))
        self.stdout.write(f'   Remaining articles: {Article.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\n🎉 Database is now clean and ready for fresh generation!'))
