# dashboard/context_processors.py
from .models import Notification

def notifications_processor(request):
    """إضافة الإشعارات غير المقروءة إلى جميع القوالب"""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by('-created_at')[:10]
        unread_count = notifications.count()
        return {
            'notifications': notifications,
            'unread_count': unread_count,
        }
    return {
        'notifications': [],
        'unread_count': 0,
    }