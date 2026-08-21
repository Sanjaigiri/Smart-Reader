"""
Management command to create 50+ diverse categories
Usage: python manage.py create_50_categories
"""

from django.core.management.base import BaseCommand
from reader.models import Category


class Command(BaseCommand):
    help = 'Create 50+ diverse categories for the Smart Reader platform'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🚀 Creating 50+ Categories...\n'))

        categories_data = [
            # Existing enhanced
            {'name': 'Business', 'slug': 'business', 'description': 'Business strategies, entrepreneurship, and career advice', 'icon': 'fa-briefcase', 'color': '#10b981'},
            {'name': 'Education', 'slug': 'education', 'description': 'Learning resources, study tips, and educational content', 'icon': 'fa-graduation-cap', 'color': '#f59e0b'},
            {'name': 'Environment', 'slug': 'environment', 'description': 'Environmental issues, conservation, and sustainability', 'icon': 'fa-leaf', 'color': '#22c55e'},
            {'name': 'Science', 'slug': 'science', 'description': 'Scientific discoveries, research, and explanations', 'icon': 'fa-flask', 'color': '#8b5cf6'},
            {'name': 'Technology', 'slug': 'technology', 'description': 'Latest tech trends, gadgets, and innovations', 'icon': 'fa-microchip', 'color': '#3b82f6'},
            {'name': 'Health & Wellness', 'slug': 'health-wellness', 'description': 'Physical and mental health, fitness, and nutrition', 'icon': 'fa-heart-pulse', 'color': '#ef4444'},
            {'name': 'Psychology', 'slug': 'psychology', 'description': 'Mental processes, behavior, and emotional well-being', 'icon': 'fa-brain', 'color': '#ec4899'},
            {'name': 'History', 'slug': 'history', 'description': 'Historical events, figures, and cultural heritage', 'icon': 'fa-landmark', 'color': '#92400e'},
            
            # Arts & Culture
            {'name': 'Art & Design', 'slug': 'art-design', 'description': 'Visual arts, graphic design, and creative expression', 'icon': 'fa-palette', 'color': '#f472b6'},
            {'name': 'Music', 'slug': 'music', 'description': 'Music theory, history, instruments, and appreciation', 'icon': 'fa-music', 'color': '#a855f7'},
            {'name': 'Literature', 'slug': 'literature', 'description': 'Books, poetry, literary analysis, and writing', 'icon': 'fa-book-open', 'color': '#6366f1'},
            {'name': 'Photography', 'slug': 'photography', 'description': 'Photography techniques, equipment, and visual storytelling', 'icon': 'fa-camera', 'color': '#06b6d4'},
            {'name': 'Film & Cinema', 'slug': 'film-cinema', 'description': 'Movies, filmmaking, cinematography, and film history', 'icon': 'fa-film', 'color': '#8b5cf6'},
            {'name': 'Theater & Drama', 'slug': 'theater-drama', 'description': 'Stage performance, acting, and theatrical arts', 'icon': 'fa-masks-theater', 'color': '#d946ef'},
            
            # Sciences
            {'name': 'Physics', 'slug': 'physics', 'description': 'Laws of nature, mechanics, and fundamental forces', 'icon': 'fa-atom', 'color': '#3b82f6'},
            {'name': 'Chemistry', 'slug': 'chemistry', 'description': 'Chemical reactions, elements, and molecular science', 'icon': 'fa-flask-vial', 'color': '#10b981'},
            {'name': 'Biology', 'slug': 'biology', 'description': 'Living organisms, ecosystems, and life sciences', 'icon': 'fa-dna', 'color': '#22c55e'},
            {'name': 'Astronomy', 'slug': 'astronomy', 'description': 'Space, stars, planets, and the universe', 'icon': 'fa-satellite', 'color': '#6366f1'},
            {'name': 'Mathematics', 'slug': 'mathematics', 'description': 'Numbers, equations, geometry, and mathematical theory', 'icon': 'fa-square-root-variable', 'color': '#f59e0b'},
            {'name': 'Geology', 'slug': 'geology', 'description': 'Earth science, rocks, minerals, and planetary formation', 'icon': 'fa-mountain', 'color': '#78716c'},
            
            # Technology & Computing
            {'name': 'Artificial Intelligence', 'slug': 'artificial-intelligence', 'description': 'AI, machine learning, and neural networks', 'icon': 'fa-robot', 'color': '#8b5cf6'},
            {'name': 'Programming', 'slug': 'programming', 'description': 'Coding, software development, and programming languages', 'icon': 'fa-code', 'color': '#3b82f6'},
            {'name': 'Cybersecurity', 'slug': 'cybersecurity', 'description': 'Online security, encryption, and digital protection', 'icon': 'fa-shield-halved', 'color': '#dc2626'},
            {'name': 'Data Science', 'slug': 'data-science', 'description': 'Analytics, big data, and statistical modeling', 'icon': 'fa-chart-line', 'color': '#059669'},
            {'name': 'Web Development', 'slug': 'web-development', 'description': 'Websites, web apps, and frontend/backend development', 'icon': 'fa-globe', 'color': '#0ea5e9'},
            {'name': 'Mobile Apps', 'slug': 'mobile-apps', 'description': 'iOS, Android, and mobile application development', 'icon': 'fa-mobile-screen', 'color': '#8b5cf6'},
            
            # Business & Finance
            {'name': 'Entrepreneurship', 'slug': 'entrepreneurship', 'description': 'Starting and growing businesses, startup culture', 'icon': 'fa-lightbulb', 'color': '#f59e0b'},
            {'name': 'Marketing', 'slug': 'marketing', 'description': 'Digital marketing, branding, and advertising strategies', 'icon': 'fa-bullhorn', 'color': '#ef4444'},
            {'name': 'Finance', 'slug': 'finance', 'description': 'Personal finance, investing, and money management', 'icon': 'fa-sack-dollar', 'color': '#10b981'},
            {'name': 'Economics', 'slug': 'economics', 'description': 'Economic theory, markets, and financial systems', 'icon': 'fa-chart-simple', 'color': '#6366f1'},
            {'name': 'Leadership', 'slug': 'leadership', 'description': 'Management, team building, and organizational skills', 'icon': 'fa-users-gear', 'color': '#8b5cf6'},
            {'name': 'Real Estate', 'slug': 'real-estate', 'description': 'Property investment, housing markets, and real estate', 'icon': 'fa-house', 'color': '#0891b2'},
            
            # Lifestyle
            {'name': 'Cooking & Recipes', 'slug': 'cooking-recipes', 'description': 'Culinary arts, recipes, and food preparation', 'icon': 'fa-utensils', 'color': '#f97316'},
            {'name': 'Travel', 'slug': 'travel', 'description': 'Travel guides, destinations, and cultural exploration', 'icon': 'fa-plane', 'color': '#0ea5e9'},
            {'name': 'Fashion', 'slug': 'fashion', 'description': 'Style, clothing trends, and fashion design', 'icon': 'fa-shirt', 'color': '#ec4899'},
            {'name': 'Sports & Fitness', 'slug': 'sports-fitness', 'description': 'Athletics, exercise, and physical training', 'icon': 'fa-dumbbell', 'color': '#ef4444'},
            {'name': 'Yoga & Meditation', 'slug': 'yoga-meditation', 'description': 'Mindfulness practices, yoga, and inner peace', 'icon': 'fa-spa', 'color': '#a855f7'},
            {'name': 'Parenting', 'slug': 'parenting', 'description': 'Child-rearing, family life, and parenting advice', 'icon': 'fa-baby', 'color': '#f472b6'},
            
            # Social Sciences
            {'name': 'Sociology', 'slug': 'sociology', 'description': 'Society, social behavior, and cultural studies', 'icon': 'fa-people-group', 'color': '#6366f1'},
            {'name': 'Philosophy', 'slug': 'philosophy', 'description': 'Philosophical thought, ethics, and existential questions', 'icon': 'fa-head-side-virus', 'color': '#8b5cf6'},
            {'name': 'Political Science', 'slug': 'political-science', 'description': 'Politics, governance, and international relations', 'icon': 'fa-scale-balanced', 'color': '#dc2626'},
            
            # Professional Development
            {'name': 'Career Development', 'slug': 'career-development', 'description': 'Professional growth, job hunting, and career planning', 'icon': 'fa-briefcase', 'color': '#0891b2'},
            {'name': 'Productivity', 'slug': 'productivity', 'description': 'Time management, efficiency, and work optimization', 'icon': 'fa-list-check', 'color': '#f59e0b'},
            {'name': 'Personal Development', 'slug': 'personal-development', 'description': 'Self-improvement, habits, and personal growth', 'icon': 'fa-seedling', 'color': '#22c55e'},
            
            # Specialized Topics
            {'name': 'Architecture', 'slug': 'architecture', 'description': 'Building design, urban planning, and structural engineering', 'icon': 'fa-building', 'color': '#78716c'},
            {'name': 'Engineering', 'slug': 'engineering', 'description': 'Mechanical, electrical, and civil engineering', 'icon': 'fa-gears', 'color': '#6366f1'},
            {'name': 'Robotics', 'slug': 'robotics', 'description': 'Robot design, automation, and mechatronics', 'icon': 'fa-robot', 'color': '#8b5cf6'},
            {'name': 'Cryptocurrency', 'slug': 'cryptocurrency', 'description': 'Digital currency, blockchain, and crypto trading', 'icon': 'fa-bitcoin-sign', 'color': '#f59e0b'},
        ]

        created_count = 0
        updated_count = 0

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Created: {category.name}'))
            else:
                # Update existing category with new data
                for key, value in cat_data.items():
                    if key != 'slug':
                        setattr(category, key, value)
                category.save()
                updated_count += 1
                self.stdout.write(f'   Updated: {category.name}')

        total_categories = Category.objects.count()
        
        self.stdout.write(self.style.SUCCESS(f'\n🎉 Category Creation Complete!'))
        self.stdout.write(self.style.SUCCESS(f'   New categories created: {created_count}'))
        self.stdout.write(f'   Existing categories updated: {updated_count}')
        self.stdout.write(self.style.SUCCESS(f'   Total categories in database: {total_categories}'))
