from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Article, Category, Tag, UserProfile, ReadingProgress,
    Note, Bookmark, Highlight, Rating, ReadingStreak,
    Achievement, UserAchievement, ReadingList, Feedback
)


# ========== CATEGORY ADMIN ==========
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'colored_icon', 'article_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def colored_icon(self, obj):
        return format_html(
            '<span style="color: {}"><i class="fas {}"></i> {}</span>',
            obj.color, obj.icon, obj.icon
        )
    colored_icon.short_description = 'Icon'
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


# ========== TAG ADMIN ==========
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


# ========== ARTICLE ADMIN ==========
class NoteInline(admin.TabularInline):
    model = Note
    extra = 0
    readonly_fields = ('user', 'selected_text', 'note', 'created_at')


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 0
    readonly_fields = ('user', 'score', 'review', 'created_at')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'difficulty', 'is_featured', 
                    'is_published', 'views_count', 'estimated_read_time', 'has_purchase_links_display', 'created_at')
    list_filter = ('category', 'difficulty', 'is_featured', 'is_published', 'created_at')
    search_fields = ('title', 'content', 'summary')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [NoteInline, RatingInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'summary', 'content')
        }),
        ('Categorization', {
            'fields': ('category', 'tags', 'difficulty')
        }),
        ('Media', {
            'fields': ('cover_image',)
        }),
        ('Author & Status', {
            'fields': ('author', 'is_featured', 'is_published')
        }),
        ('Related Book Purchase Links', {
            'fields': ('book_title', 'amazon_link', 'flipkart_link', 'meesho_link'),
            'description': '\u26a0\ufe0f Only fill these fields if a related book is available for purchase. Leave empty if no book exists.',
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('views_count', 'estimated_read_time'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('estimated_read_time',)
    
    def has_purchase_links_display(self, obj):
        return obj.has_purchase_links()
    has_purchase_links_display.boolean = True
    has_purchase_links_display.short_description = '\ud83d\uded2 Purchase Available'
    
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


# ========== USER PROFILE ADMIN ==========
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'reading_goal', 'language', 'theme', 'dark_mode', 'created_at')
    list_filter = ('language', 'theme', 'dark_mode', 'created_at')
    search_fields = ('user__username', 'user__email')


# ========== READING PROGRESS ADMIN ==========
@admin.register(ReadingProgress)
class ReadingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'scroll_percentage', 'time_spent_formatted', 
                    'is_completed', 'last_read_at')
    list_filter = ('is_completed', 'last_read_at')
    search_fields = ('user__username', 'article__title')
    date_hierarchy = 'last_read_at'
    
    def time_spent_formatted(self, obj):
        hours = obj.time_spent // 3600
        minutes = (obj.time_spent % 3600) // 60
        seconds = obj.time_spent % 60
        if hours:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"
    time_spent_formatted.short_description = 'Time Spent'


# ========== NOTE ADMIN ==========
@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'note_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title', 'note', 'selected_text')
    date_hierarchy = 'created_at'
    
    def note_preview(self, obj):
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'Note'


# ========== BOOKMARK ADMIN ==========
@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title')


# ========== HIGHLIGHT ADMIN ==========
@admin.register(Highlight)
class HighlightAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'text_preview', 'color', 'created_at')
    list_filter = ('color', 'created_at')
    search_fields = ('user__username', 'article__title', 'text')
    
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Highlighted Text'


# ========== RATING ADMIN ==========
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'score_display', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'article__title')
    
    def score_display(self, obj):
        return '⭐' * obj.score
    score_display.short_description = 'Rating'


# ========== READING STREAK ADMIN ==========
@admin.register(ReadingStreak)
class ReadingStreakAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_streak', 'longest_streak', 'total_reading_days', 'last_read_date')
    list_filter = ('last_read_date',)
    search_fields = ('user__username',)
    ordering = ('-current_streak',)


# ========== ACHIEVEMENT ADMIN ==========
@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'requirement_type', 'requirement_value', 'badge_color')
    list_filter = ('requirement_type',)
    search_fields = ('name', 'description')


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement', 'earned_at')
    list_filter = ('achievement', 'earned_at')
    search_fields = ('user__username', 'achievement__name')


# ========== READING LIST ADMIN ==========
@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'article_count', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('name', 'user__username')
    filter_horizontal = ('articles',)
    
    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


# ========== FEEDBACK ADMIN ==========
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'feedback_preview', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('user__username', 'article__title', 'feedback_text')
    date_hierarchy = 'created_at'
    readonly_fields = ('user', 'article', 'feedback_text', 'is_helpful', 'created_at')
    
    def feedback_preview(self, obj):
        return obj.feedback_text[:75] + '...' if len(obj.feedback_text) > 75 else obj.feedback_text
    feedback_preview.short_description = 'Feedback'
    
    def has_add_permission(self, request):
        return False  # Feedback is only added by users


# ========== CUSTOMIZE ADMIN SITE ==========
admin.site.site_header = "📚 SmartReader Administration"
admin.site.site_title = "SmartReader Admin"
admin.site.index_title = "Welcome to SmartReader Admin Panel"
