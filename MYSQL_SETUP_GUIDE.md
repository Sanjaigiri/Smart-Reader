# MySQL Database Setup Guide for SmartReader

## Complete Guide to Connect SmartReader with MySQL via XAMPP

### Prerequisites
- XAMPP installed on your system
- Django project running (SmartReader)
- Python MySQL client library

---

## Step 1: Install MySQL Client for Python

Open terminal in your project directory and run:

```bash
# For Windows (using pip)
pip install mysqlclient

# If mysqlclient fails, try PyMySQL as alternative:
pip install pymysql

# If using PyMySQL, add this to smart_reader/__init__.py:
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Step 2: Start XAMPP MySQL Server

1. Open **XAMPP Control Panel**
2. Click **Start** button next to **Apache**
3. Click **Start** button next to **MySQL**
4. Both should show green "Running" status

---

## Step 3: Create Database in phpMyAdmin

1. Open your browser and go to: **http://localhost/phpmyadmin**
2. Click on **"New"** in the left sidebar
3. Database name: **`smartreader`**
4. Collation: **`utf8mb4_general_ci`**
5. Click **"Create"**

✅ Your database is now created!

---

## Step 4: Configure Django to Use MySQL

### Option A: Using Environment Variables (.env file)

1. Copy `.env.example` to `.env` (if not already done):
   ```bash
   copy .env.example .env
   ```

2. Edit the `.env` file and set:
   ```env
   DATABASE_TYPE=mysql
   DB_NAME=smartreader
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=localhost
   DB_PORT=3306
   ```

### Option B: Direct Configuration (not recommended)

Edit `smart_reader/settings.py` and uncomment the MySQL configuration.

---

## Step 5: Run Migrations

This will create all necessary tables in your MySQL database:

```bash
# Navigate to smart_reader directory
cd smart_reader

# Run migrations
python manage.py migrate
```

You should see output like:
```
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying reader.0001_initial... OK
  ...
```

---

## Step 6: Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: (your choice)
- Email: sanjaigiri001@gmail.com (or your email)
- Password: (secure password)

---

## Step 7: Verify Database Connection

Run this command to check database connection:

```bash
python manage.py dbshell
```

If successful, you'll see MySQL prompt:
```
mysql>
```

Type `exit` to quit.

---

## Step 8: View Your Data in phpMyAdmin

1. Go to **http://localhost/phpmyadmin**
2. Click on **`smartreader`** database in left sidebar
3. You should see all tables created:
   - `auth_user` - User accounts
   - `reader_userprofile` - User profiles
   - `reader_article` - Articles
   - `reader_readingprogress` - Reading progress tracking
   - `reader_bookmark` - User bookmarks
   - And many more...

---

## Database Schema Overview

### Key Tables:

#### 1. `auth_user` - User Accounts
- `id` - User ID (primary key)
- `username` - Username
- `email` - Email address
- `password` - Hashed password
- `first_name` - First name
- `is_staff` - Admin status
- `date_joined` - Registration date

#### 2. `reader_userprofile` - User Profiles
- `id` - Profile ID
- `user_id` - Foreign key to auth_user
- `bio` - User biography
- `reading_goal` - Weekly reading goal
- `is_email_verified` - Email verification status
- `language` - Preferred language
- `theme` - Light/Dark mode

#### 3. `reader_article` - Articles
- `id` - Article ID
- `title` - Article title
- `slug` - URL-friendly slug
- `content` - Article content (HTML)
- `category_id` - Foreign key to category
- `author_id` - Foreign key to auth_user
- `views_count` - View counter
- `is_published` - Published status
- `created_at` - Creation date

#### 4. `reader_readingprogress` - Reading Tracking
- `id` - Progress ID
- `user_id` - Foreign key to auth_user
- `article_id` - Foreign key to reader_article
- `scroll_percentage` - Current scroll position
- `max_scroll_percentage` - Highest reached (only increases)
- `time_spent` - Time spent in seconds
- `is_completed` - Completion status
- `last_read_at` - Last reading timestamp

#### 5. `reader_bookmark` - User Bookmarks
- `id` - Bookmark ID
- `user_id` - Foreign key to auth_user
- `article_id` - Foreign key to reader_article
- `created_at` - Bookmark date

---

## Useful MySQL Queries

### Check Total Users:
```sql
SELECT COUNT(*) as total_users FROM auth_user;
```

### Check Total Articles:
```sql
SELECT COUNT(*) as total_articles FROM reader_article WHERE is_published = 1;
```

### Get User Reading Statistics:
```sql
SELECT 
    u.username,
    u.email,
    COUNT(rp.id) as articles_read,
    SUM(rp.time_spent) as total_time_seconds,
    SUM(CASE WHEN rp.is_completed = 1 THEN 1 ELSE 0 END) as completed_articles
FROM auth_user u
LEFT JOIN reader_readingprogress rp ON u.id = rp.user_id
GROUP BY u.id
ORDER BY articles_read DESC;
```

### Get Articles Read by Specific User:
```sql
SELECT 
    a.title,
    rp.scroll_percentage,
    rp.is_completed,
    rp.time_spent,
    rp.last_read_at
FROM reader_readingprogress rp
JOIN reader_article a ON rp.article_id = a.id
JOIN auth_user u ON rp.user_id = u.id
WHERE u.email = 'user@example.com'
ORDER BY rp.last_read_at DESC;
```

### Get Top 10 Most Read Articles:
```sql
SELECT 
    a.title,
    a.views_count,
    COUNT(rp.id) as readers,
    SUM(rp.time_spent) as total_reading_time
FROM reader_article a
LEFT JOIN reader_readingprogress rp ON a.id = rp.article_id
WHERE a.is_published = 1
GROUP BY a.id
ORDER BY a.views_count DESC
LIMIT 10;
```

---

## Backup Your Database

### Create Backup:
```bash
# From command line (requires mysqldump)
mysqldump -u root smartreader > backup_smartreader.sql
```

### Restore Backup:
```bash
mysql -u root smartreader < backup_smartreader.sql
```

---

## Troubleshooting

### Error: "No module named 'MySQLdb'"
**Solution**: Install mysqlclient or pymysql
```bash
pip install mysqlclient
```

### Error: "Access denied for user 'root'@'localhost'"
**Solution**: Check MySQL password in .env file or settings.py

### Error: "Can't connect to MySQL server"
**Solution**: 
1. Make sure XAMPP MySQL is running
2. Check port 3306 is not blocked by firewall
3. Verify DB_HOST=localhost in .env

### Error: "Unknown database 'smartreader'"
**Solution**: Create the database in phpMyAdmin first

### Tables not created after migration
**Solution**: 
```bash
python manage.py migrate --run-syncdb
```

---

## Testing Database Connection

Create a test file `test_mysql_connection.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_reader.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ Connected to MySQL!")
        print(f"MySQL Version: {version[0]}")
        
        # Check tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"\n📊 Total Tables: {len(tables)}")
        print("\nTables:")
        for table in tables:
            print(f"  - {table[0]}")
            
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

Run it:
```bash
python test_mysql_connection.py
```

---

## Complete Setup Checklist

- [ ] XAMPP installed
- [ ] MySQL service running in XAMPP
- [ ] mysqlclient or pymysql installed
- [ ] Database 'smartreader' created in phpMyAdmin
- [ ] .env file configured with DATABASE_TYPE=mysql
- [ ] Migrations run successfully
- [ ] Superuser created
- [ ] Test connection successful
- [ ] Can view tables in phpMyAdmin

---

## Switch Back to SQLite

If you want to switch back to SQLite:

1. Edit `.env` file:
   ```env
   DATABASE_TYPE=sqlite
   ```

2. Restart Django server

That's it! The app will use SQLite database (db.sqlite3) instead.

---

## Summary

✅ **Current Database**: Check your `.env` file
- `DATABASE_TYPE=sqlite` → Using SQLite (db.sqlite3)
- `DATABASE_TYPE=mysql` → Using MySQL (smartreader database)

✅ **View Data**: http://localhost/phpmyadmin (for MySQL)

✅ **Admin Panel**: http://127.0.0.1:8000/admin-dashboard/

✅ **User Data Tracking**: All reading progress, bookmarks, and user activities are stored in the database with complete tracking.

---

Need help? Check the error messages and refer to the Troubleshooting section above! 🚀
