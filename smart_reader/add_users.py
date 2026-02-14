import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.contrib.auth.models import User
from reader.models import UserProfile

def create_users():
    """Create 5 test users with profiles"""
    
    users_data = [
        {
            'username': 'john_doe',
            'email': 'john.doe@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'password': 'password123',
            'bio': 'Avid reader and tech enthusiast',
            'reading_goal': 7
        },
        {
            'username': 'jane_smith',
            'email': 'jane.smith@example.com',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'password': 'password123',
            'bio': 'Love reading fiction and self-help books',
            'reading_goal': 10
        },
        {
            'username': 'mike_wilson',
            'email': 'mike.wilson@example.com',
            'first_name': 'Mike',
            'last_name': 'Wilson',
            'password': 'password123',
            'bio': 'Science and technology reader',
            'reading_goal': 5
        },
        {
            'username': 'sarah_jones',
            'email': 'sarah.jones@example.com',
            'first_name': 'Sarah',
            'last_name': 'Jones',
            'password': 'password123',
            'bio': 'Book club member and literature lover',
            'reading_goal': 12
        },
        {
            'username': 'alex_brown',
            'email': 'alex.brown@example.com',
            'first_name': 'Alex',
            'last_name': 'Brown',
            'password': 'password123',
            'bio': 'Philosophy and history enthusiast',
            'reading_goal': 8
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        # Check if user already exists
        if User.objects.filter(username=user_data['username']).exists():
            print(f"❌ User '{user_data['username']}' already exists. Skipping...")
            continue
        
        if User.objects.filter(email=user_data['email']).exists():
            print(f"❌ Email '{user_data['email']}' already exists. Skipping...")
            continue
        
        # Create user
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            password=user_data['password']
        )
        
        # Create or update user profile
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.bio = user_data['bio']
        profile.reading_goal = user_data['reading_goal']
        profile.is_email_verified = True  # Mark as verified for testing
        profile.save()
        
        created_users.append(user_data['username'])
        print(f"✅ Created user: {user_data['username']} ({user_data['email']})")
    
    print(f"\n{'='*60}")
    print(f"Successfully created {len(created_users)} users!")
    print(f"{'='*60}")
    
    if created_users:
        print("\nUser Details:")
        print("-" * 60)
        print(f"{'Username':<20} {'Email':<30} {'Password'}")
        print("-" * 60)
        for user_data in users_data:
            if user_data['username'] in created_users:
                print(f"{user_data['username']:<20} {user_data['email']:<30} password123")
        print("-" * 60)
        print("\nYou can now login with any of these credentials!")

if __name__ == '__main__':
    try:
        create_users()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
