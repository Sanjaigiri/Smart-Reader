# Smart Reader Database - Quick Reference

## 🎯 What You Have Now

You have **3 powerful scripts** to query your smart_reader database:

### 📊 Script 1: Complete Database Viewer
**File**: `view_database_records.py`
```bash
python view_database_records.py           # View everything
python view_database_records.py sanjai    # View specific user
```

**Shows**:
- ✅ All users and profiles
- ✅ Admin users
- ✅ Signup/login details
- ✅ All articles (107,453 total!)
- ✅ User progress for everyone

---

### 🔍 Script 2: User Progress Checker
**File**: `check_user_progress.py`
```bash
python check_user_progress.py sanjai
```

**Shows**:
- 📋 Basic info (name, email, status)
- 📊 Reading statistics (11 articles started, 45.5% completed)
- 🔥 Reading streak (3 days current)
- 📚 Bookmarks, notes, highlights
- 🏆 Achievements earned
- 📖 Detailed progress per article

---

### 💻 Script 3: Interactive Query Tool
**File**: `query_database.py`
```bash
python query_database.py
```

**Features**:
1. List all users
2. Search for users
3. View user progress
4. View all records
5. Exit

---

## 📈 Current Database Status

### Users (5 Total)
| Username | Type | Email | Status |
|----------|------|-------|--------|
| sanjai | Admin | sanjaigiri001@gmail.com | Most Active ⭐ |
| giri | Admin | sanjaig111@gmail.com | Active |
| testuser123 | User | testuser123@example.com | Active |
| 23bcs052 | User | 23bcs052@kprcas.ac.in | Active |
| mr.thirumoorthys | User | mr.thirumoorthys@gmail.com | Active |

---

### Articles (107,453 Total!)
| Category | Articles | Featured |
|----------|----------|----------|
| History | 13,343 | Yes |
| Health & Wellness | 13,339 | Yes |
| Psychology | 13,324 | Yes |
| Science | 13,345 | Yes |
| Technology | 13,344 | Yes |
| Education | 13,344 | Yes |
| Environment | 13,341 | Yes |
| Business | 13,333 | Yes |
| **Others** | ~800 | Some |

---

### Top User: sanjai 🏆

**Reading Stats**:
- 📖 11 articles started
- ✅ 5 completed (45.5%)
- ⏳ 6 in progress
- ⏱️ 1h 18m total reading time
- 📊 85.4% average progress

**Engagement**:
- 🔥 3-day current streak
- 📌 2 bookmarks
- 📝 8 notes created
- 🖍️ 5 text highlights
- ⭐ 6 ratings (4.3⭐ average)
- 🏆 3 achievements earned

**Recent Activity**:
1. ✅ Explore Your Creativity (100%)
2. ⏳ Rich Dad Poor Dad (72%)
3. ⏳ Glaciology and Ice Ages (88%)
4. ✅ Understanding AI (100%)
5. ✅ Explore Analytical Skills (100%)

---

## 🚀 Quick Start Commands

### View Everything
```bash
cd d:\Django\Final_Sem\smart_reader
python view_database_records.py
```

### Check User "sanjai"
```bash
python check_user_progress.py sanjai
```

### Check User "giri"
```bash
python check_user_progress.py giri
```

### Interactive Mode
```bash
python query_database.py
```

---

## 🎯 Common Use Cases

### 1. "I want to see all users"
```bash
python query_database.py
# Select option 1
```

### 2. "I want to check if a user is progressing"
```bash
python check_user_progress.py <username>
```

### 3. "I want to see all articles"
```bash
python view_database_records.py
# Scroll to ARTICLES section
```

### 4. "I want to find a user by email"
```bash
python query_database.py
# Select option 2
# Enter email (partial works!)
```

### 5. "I want to see admin list"
```bash
python view_database_records.py
# Scroll to ADMIN USERS section
```

### 6. "I want to see login history"
```bash
python view_database_records.py
# Scroll to SIGNUP & LOGIN DETAILS
```

---

## 📊 What Each User Has Done

### testuser123
- Status: Active but not reading yet
- Progress: 0 articles
- Reading Lists: 1 created (web development)

### sanjai (MOST ACTIVE) ⭐
- Status: Super active reader
- Progress: 11 articles (5 completed)
- Time: 1h 18m
- Streak: 3 days
- Achievements: 3 earned
- Notes: 8 created
- Reading Lists: 1 (Python study)

### giri
- Status: Started reading
- Progress: 1 article (86% completed)
- Time: 8m 2s
- Notes: 1 created
- Streak: 1 day

### 23bcs052
- Status: Registered but no activity
- Progress: 0 articles

### mr.thirumoorthys
- Status: Registered but no activity
- Progress: 0 articles

---

## 🔑 Key Insights

1. **Total Users**: 5 registered
2. **Active Readers**: 2 (sanjai, giri)
3. **Total Articles**: 107,453 available
4. **Most Read Categories**: History, Health, Science, Technology
5. **Average Completion Rate**: ~45% (based on active users)
6. **Total Reading Time**: ~1.5 hours combined
7. **OTP Verifications**: 9 attempted (0 verified)

---

## 📂 Files Created

All files are in: `d:\Django\Final_Sem\smart_reader\`

1. ✅ `view_database_records.py` - Complete database viewer
2. ✅ `check_user_progress.py` - Individual user progress
3. ✅ `query_database.py` - Interactive query tool
4. ✅ `DATABASE_QUERY_GUIDE.md` - Detailed documentation
5. ✅ `DATABASE_SUMMARY.md` - This quick reference

---

## 💡 Pro Tips

1. **Regular users**: Use `check_user_progress.py <username>`
2. **Quick overview**: Use `view_database_records.py`
3. **Exploring**: Use `query_database.py` (interactive)
4. **Searching**: Interactive tool has search feature
5. **Specific data**: All scripts output to console (can redirect to file)

---

## 📞 Example Session

```bash
# Start
cd d:\Django\Final_Sem\smart_reader

# Check what users exist
python view_database_records.py | findstr "Username:"

# Pick a user and check progress
python check_user_progress.py sanjai

# Interactive exploration
python query_database.py
```

---

## ✅ Summary

You now have:
- ✅ Database connection established
- ✅ User records accessible
- ✅ Admin details viewable
- ✅ Article information retrievable
- ✅ Individual user progress trackable
- ✅ Interactive query tool available
- ✅ Complete documentation

**Database**: smart_reader
**Location**: D:\Django\Final_Sem\smart_reader\db.sqlite3
**Records**: 5 users, 107,453 articles, detailed progress tracking

---

**Last Updated**: January 24, 2026
**Status**: ✅ All systems operational
