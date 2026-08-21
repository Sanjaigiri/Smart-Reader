from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


# ========== USER PROFILE ==========
class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'हिंदी (Hindi)'),
        ('ta', 'தமிழ் (Tamil)'),
        ('te', 'తెలుగు (Telugu)'),
        ('bn', 'বাংলা (Bengali)'),
        ('mr', 'मराठी (Marathi)'),
        ('gu', 'ગુજરાતી (Gujarati)'),
        ('kn', 'ಕನ್ನಡ (Kannada)'),
        ('ml', 'മലയാളം (Malayalam)'),
        ('pa', 'ਪੰਜਾਬੀ (Punjabi)'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light Mode'),
        ('dark', 'Dark Mode'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True)
    reading_goal = models.IntegerField(default=5)  # articles per week
    preferred_font_size = models.IntegerField(default=16)
    dark_mode = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Language and theme preferences
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en', help_text='Preferred language for the interface')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light', help_text='Preferred theme (light or dark mode)')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


# ========== OTP VERIFICATION ==========
class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"OTP for {self.email}"
    
    @staticmethod
    def generate_otp():
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    class Meta:
        ordering = ['-created_at']


# ========== SITE VISIT TRACKING ==========
class SiteVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    visit_date = models.DateField(auto_now_add=True)
    visit_time = models.DateTimeField(auto_now_add=True)
    page_visited = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-visit_time']
    
    def __str__(self):
        return f"Visit on {self.visit_date} - {self.user or 'Anonymous'}"


# ========== ARTICLE VIEW LOG ==========
class ArticleViewLog(models.Model):
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='view_logs')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)
    time_spent = models.IntegerField(default=0)  # seconds
    
    class Meta:
        ordering = ['-viewed_at']
    
    def __str__(self):
        return f"{self.article.title} viewed by {self.user or 'Anonymous'}"


# ========== CATEGORY & TAGS ==========
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-folder')  # FontAwesome icon
    color = models.CharField(max_length=7, default='#6366f1')  # Hex color
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name


# ========== ARTICLE ==========
class Article(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    summary = models.TextField(max_length=500, blank=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='articles')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    estimated_read_time = models.IntegerField(default=5)  # minutes
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Purchase links for related books
    amazon_link = models.URLField(max_length=500, blank=True, null=True, help_text="Amazon purchase link for related book")
    flipkart_link = models.URLField(max_length=500, blank=True, null=True, help_text="Flipkart purchase link for related book")
    meesho_link = models.URLField(max_length=500, blank=True, null=True, help_text="Meesho purchase link for related book")
    book_title = models.CharField(max_length=200, blank=True, null=True, help_text="Title of the related book")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def has_purchase_links(self):
        """Check if any purchase link is available"""
        return bool(self.amazon_link or self.flipkart_link or self.meesho_link)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            self.slug = base_slug
            
            # Handle duplicate slugs by adding a unique suffix
            counter = 1
            while Article.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Calculate estimated read time (avg 200 words/min)
        word_count = len(self.content.split())
        self.estimated_read_time = max(1, word_count // 200)
        super().save(*args, **kwargs)


# ========== READING PROGRESS ==========
class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_progress')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='progress')
    last_position = models.IntegerField(default=0)
    scroll_percentage = models.IntegerField(default=0)
    max_scroll_percentage = models.IntegerField(default=0)  # Highest percentage reached (only increases)
    time_spent = models.IntegerField(default=0)  # seconds
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True, null=True)
    last_read_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ['user', 'article']

    def __str__(self):
        return f"{self.user.username} - {self.article.title} ({self.max_scroll_percentage}%)"
    
    def update_progress(self, new_percentage, position=0, time=0):
        """Update progress - percentage only increases, never decreases"""
        self.last_position = position
        self.scroll_percentage = new_percentage
        
        # Only update max if new percentage is higher
        if new_percentage > self.max_scroll_percentage:
            self.max_scroll_percentage = new_percentage
        
        self.time_spent += time
        
        # Mark as completed if max reached 90% or user reached 100%
        if self.max_scroll_percentage >= 90 or new_percentage >= 100:
            self.is_completed = True
        
        self.save()


# ========== BOOKMARKS ==========
class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'article']
    
    def __str__(self):
        return f"{self.user.username} - {self.article.title}"


# ========== HIGHLIGHTS ==========
class Highlight(models.Model):
    COLORS = [
        ('yellow', 'Yellow'),
        ('green', 'Green'),
        ('blue', 'Blue'),
        ('pink', 'Pink'),
        ('orange', 'Orange'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='highlights')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='highlights')
    text = models.TextField()
    color = models.CharField(max_length=20, choices=COLORS, default='yellow')
    start_offset = models.IntegerField(default=0)
    end_offset = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.text[:50]}..."


# ========== NOTES ==========
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='notes')
    highlight = models.ForeignKey(Highlight, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    selected_text = models.TextField(blank=True)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note by {self.user.username} on {self.article.title}"


# ========== RATINGS & REVIEWS ==========
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'article']
    
    def __str__(self):
        return f"{self.user.username} - {self.article.title}: {self.score}★"


# ========== FEEDBACK ==========
class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedbacks')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_text = models.TextField()
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback by {self.user.username} on {self.article.title}"


# ========== READING STREAK & ACHIEVEMENTS ==========
class ReadingStreak(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='streak')
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_read_date = models.DateField(null=True, blank=True)
    total_reading_days = models.IntegerField(default=0)
    
    def update_streak(self):
        today = timezone.now().date()
        if self.last_read_date:
            diff = (today - self.last_read_date).days
            if diff == 1:
                self.current_streak += 1
            elif diff > 1:
                self.current_streak = 1
        else:
            self.current_streak = 1
        
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.last_read_date = today
        self.total_reading_days += 1
        self.save()


class Achievement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50)
    badge_color = models.CharField(max_length=7, default='#fbbf24')
    requirement_type = models.CharField(max_length=50)  # articles_read, streak_days, time_spent
    requirement_value = models.IntegerField()
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']


# ========== READING LIST / COLLECTION ==========
class ReadingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_lists')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    articles = models.ManyToManyField(Article, blank=True, related_name='in_lists')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"

