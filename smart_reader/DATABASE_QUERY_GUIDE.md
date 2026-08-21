# Database Query Tools for Smart Reader

This document explains how to connect to the database and view all records including users, admins, articles, and user progress.

## Database Information

- **Database Name**: smart_reader
- **Database Type**: SQLite3
- **Database Location**: `d:\Django\Final_Sem\smart_reader\db.sqlite3`
- **Django Settings**: `smart_reader.settings`

## Available Scripts

### 1. View All Database Records
**Script**: `view_database_records.py`

Displays comprehensive information about:
- All users and their profiles
- Admin users
- Signup and login details
- All articles
- User reading progress for all users

**Usage**:
```bash
cd d:\Django\Final_Sem\smart_reader
python view_database_records.py
```

**To view specific user**:
```bash
python view_database_records.py <username>
```

**Example**:
```bash
python view_database_records.py sanjai
```

---

### 2. Check Individual User Progress
**Script**: `check_user_progress.py`

Displays detailed progress report for a specific user including:
- Basic user information
- Profile settings
- Reading statistics
- Reading streak
- Recent activity
- Completed articles
- In-progress articles
- Bookmarks
- Achievements
- Notes
- Reading lists

**Usage**:
```bash
python check_user_progress.py <username>
```

**Examples**:
```bash
python check_user_progress.py sanjai
python check_user_progress.py testuser123
python check_user_progress.py giri
```

---

### 3. Interactive Database Query Tool
**Script**: `query_database.py`

Interactive menu-driven tool with options:
1. List all users
2. Search for a user
3. View specific user progress
4. View all database records
5. Exit

**Usage**:
```bash
python query_database.py
```

Then follow the menu prompts.

---

## Database Tables and Data

### User Tables
- **auth_user**: Django default user table (username, email, password, etc.)
- **reader_userprofile**: Extended user profile (bio, reading goal, preferences)

### Authentication Tables
- **reader_otpverification**: OTP records for email verification

### Article Tables
- **reader_article**: All articles with content, metadata
- **reader_category**: Article categories
- **reader_tag**: Article tags

### Reading Progress Tables
- **reader_readingprogress**: User reading progress per article
- **reader_bookmark**: User bookmarks
- **reader_readingstreak**: User reading streaks
- **reader_highlight**: Text highlights
- **reader_note**: User notes on articles
- **reader_rating**: User ratings and reviews

### Achievement Tables
- **reader_achievement**: Available achievements
- **reader_userachievement**: Achievements earned by users

### Other Tables
- **reader_readinglist**: User-created reading lists
- **reader_sitevisit**: Site visit tracking
- **reader_articleviewlog**: Article view logs
- **reader_feedback**: User feedback

---

## Current Database Statistics

Based on the latest query:

### Users
- **Total Users**: 5
- **Active Users**: 5
- **Admin Users**: 2 (sanjai, giri)
- **Regular Users**: 3

### Articles
- **Total Articles**: 107,453
- **Published Articles**: 107,453
- **Featured Articles**: 1,195
- **Total Categories**: 61

### Top Active User (sanjai)
- **Reading Progress**: 11 articles started
- **Completed**: 5 articles (45.5%)
- **In Progress**: 6 articles
- **Total Reading Time**: 1h 18m
- **Current Streak**: 3 days
- **Bookmarks**: 2
- **Notes**: 8
- **Highlights**: 5
- **Achievements**: 3

---

## How to Check User Progress

### Method 1: Quick Check for Specific User
```bash
python check_user_progress.py sanjai
```

### Method 2: Interactive Search
```bash
python query_database.py
# Then select option 2 or 3
```

### Method 3: View All Users First
```bash
python view_database_records.py
# Scroll through the output to see all users
```

### Method 4: Search by Email
```bash
python query_database.py
# Select option 2
# Enter email address (partial match works)
```

---

## Querying Specific Information

### Get All Admin Users
```bash
python view_database_records.py
# Scroll to "ADMIN USERS" section
```

### Get Signup/Login History
```bash
python view_database_records.py
# Scroll to "SIGNUP & LOGIN DETAILS" section
```

### Get Article Statistics
```bash
python view_database_records.py
# Scroll to "ARTICLES" section
```

### Get User Reading Patterns
```bash
python check_user_progress.py <username>
# View detailed reading activity
```

---

## Available Users in Database

Current users (as of last check):

1. **testuser123** (Regular User)
   - Email: testuser123@example.com
   - Joined: 2025-12-27

2. **sanjai** (Admin)
   - Email: sanjaigiri001@gmail.com
   - Joined: 2025-12-27
   - Most active user

3. **giri** (Admin)
   - Email: sanjaig111@gmail.com
   - Joined: 2025-12-27

4. **23bcs052** (Regular User)
   - Email: 23bcs052@kprcas.ac.in
   - Joined: 2026-01-05

5. **mr.thirumoorthys** (Regular User)
   - Email: mr.thirumoorthys@gmail.com
   - Joined: 2026-01-05

---

## Database Connection Details

The scripts automatically connect to the database using Django ORM. No manual connection required.

**Connection Configuration** (in `settings.py`):
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

---

## Tips

1. **To see all users**: Run `python query_database.py` and select option 1
2. **To search users**: Run `python query_database.py` and select option 2
3. **For detailed report**: Use `python check_user_progress.py <username>`
4. **For overview**: Use `python view_database_records.py`

---

## Troubleshooting

### Error: "Module not found"
Make sure you're in the correct directory:
```bash
cd d:\Django\Final_Sem\smart_reader
```

### Error: "User not found"
Check available users first:
```bash
python check_user_progress.py
# Without arguments, it will list available users
```

### Error: "Django settings module"
Ensure the virtual environment is activated:
```bash
.venv\Scripts\Activate.ps1
```

---

## Quick Commands Reference

```bash
# View all records
python view_database_records.py

# Check specific user
python check_user_progress.py sanjai

# Interactive mode
python query_database.py

# View user without progress details
python view_database_records.py sanjai
```

---

## Created By
Script created on: January 24, 2026
Database: smart_reader
Location: D:\Django\Final_Sem\smart_reader\
