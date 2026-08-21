"""
Test the database connection and display summary
"""
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.contrib.auth.models import User
from reader.models import Article, ReadingProgress

print("\n" + "="*80)
print(" "*30 + "DATABASE TEST")
print("="*80)

print("\n✅ Database Connection: SUCCESS")
print(f"✅ Total Users: {User.objects.count()}")
print(f"✅ Total Articles: {Article.objects.count()}")
print(f"✅ Reading Progress Records: {ReadingProgress.objects.count()}")

print("\n" + "="*80)
print("Database is connected and working properly!")
print("="*80 + "\n")
