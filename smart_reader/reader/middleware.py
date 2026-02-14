from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import SiteVisit


class VisitTrackingMiddleware(MiddlewareMixin):
    """Middleware to track site visits for analytics"""
    
    def process_request(self, request):
        # Skip tracking for static files, media files, and admin panel
        if any([
            request.path.startswith('/static/'),
            request.path.startswith('/media/'),
            request.path.startswith('/admin/'),
            request.path.startswith('/favicon.ico'),
        ]):
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Track the visit
        try:
            SiteVisit.objects.create(
                user=request.user if request.user.is_authenticated else None,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                page_visited=request.path[:255]
            )
        except Exception as e:
            # Silently fail to not break the site
            pass
        
        return None
