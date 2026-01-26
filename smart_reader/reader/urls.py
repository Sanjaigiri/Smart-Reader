from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('check-email/', views.check_email, name='check_email'),
    
    # Articles
    path('articles/', views.article_list, name='articles'),
    path('article/<slug:slug>/', views.article_detail, name='article_detail'),
    path('read/<int:id>/', views.read_article, name='read'),  # Legacy support
    path('download/<int:article_id>/', views.download_article_pdf, name='download_article'),
    
    # Reading Progress
    path('save-progress/', views.save_progress, name='save_progress'),
    path('my-progress/', views.my_progress, name='my_progress'),
    
    # Notes
    path('save-note/', views.save_note, name='save_note'),
    path('delete-note/<int:note_id>/', views.delete_note, name='delete_note'),
    path('my-notes/', views.my_notes, name='my_notes'),
    path('quick-note/', views.quick_note, name='quick_note'),
    
    # Bookmarks
    path('toggle-bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    
    # Highlights
    path('save-highlight/', views.save_highlight, name='save_highlight'),
    path('delete-highlight/<int:highlight_id>/', views.delete_highlight, name='delete_highlight'),
    path('my-highlights/', views.my_highlights, name='my_highlights'),
    
    # Ratings
    path('rate-article/', views.rate_article, name='rate_article'),
    
    # Feedback
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    
    # Search Autocomplete
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
    
    # User Dashboard & Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    
    # Language & Theme
    path('change-language/', views.change_language, name='change_language'),
    path('change-theme/', views.change_theme, name='change_theme'),
    
    # Reading Lists
    path('reading-lists/', views.reading_lists, name='reading_lists'),
    path('add-to-list/', views.add_to_list, name='add_to_list'),
    path('remove-from-list/<int:list_id>/<int:article_id>/', views.remove_from_list, name='remove_from_list'),
    path('delete-list/<int:list_id>/', views.delete_reading_list, name='delete_reading_list'),
    
    # Streaks & Achievements
    path('my-streaks/', views.my_streaks, name='my_streaks'),
    path('my-achievements/', views.my_achievements, name='my_achievements'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # API
    path('api/user-stats/', views.get_user_stats, name='user_stats'),
    
    # Admin Dashboard
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users, name='admin_users'),
    path('admin-panel/users/toggle/<int:user_id>/', views.admin_toggle_user_status, name='admin_toggle_user'),
    path('admin-panel/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    path('admin-panel/articles/', views.admin_articles, name='admin_articles'),
    path('admin-panel/articles/add/', views.admin_add_article, name='admin_add_article'),
    path('admin-panel/articles/edit/<int:article_id>/', views.admin_edit_article, name='admin_edit_article'),
    path('admin-panel/articles/delete/<int:article_id>/', views.admin_delete_article, name='admin_delete_article'),
    path('admin-panel/analytics/', views.admin_analytics, name='admin_analytics'),
    path('admin-panel/feedbacks/', views.admin_feedbacks, name='admin_feedbacks'),
]
