# Context processors for the reader app
ADMIN_EMAILS = ['sanjaigiri001@gmail.com', 'sanjaig111@gmail.com']

def admin_check(request):
    """Add is_admin flag to template context"""
    is_admin = False
    if request.user.is_authenticated:
        is_admin = (
            request.user.is_staff or 
            request.user.is_superuser or 
            request.user.email in ADMIN_EMAILS
        )
    return {
        'is_admin_user': is_admin
    }
