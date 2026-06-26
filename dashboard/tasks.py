from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from dashboard.models import Notification
from graduates.models import Graduate

@shared_task
def send_email_notification(subject, message, recipient_email):
    """إرسال بريد إلكتروني"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
        )
        return f"✅ Email sent to {recipient_email}"
    except Exception as e:
        return f"❌ Failed to send email: {e}"

@shared_task
def send_push_notification(user_id, title, message, url='/'):
    """إرسال إشعار فوري (Push)"""
    from webpush import send_user_notification
    from django.contrib.auth.models import User
    
    try:
        user = User.objects.get(id=user_id)
        payload = {
            'head': title,
            'body': message,
            'url': url,
        }
        send_user_notification(user=user, payload=payload)
        return f"✅ Push notification sent to {user.username}"
    except Exception as e:
        return f"❌ Failed to send push: {e}"

@shared_task
def check_expired_jobs():
    """التحقق من الوظائف المنتهية الصلاحية وإرسال تنبيهات"""
    from jobs.models import Job
    from django.utils import timezone
    
    expired = Job.objects.filter(deadline__lt=timezone.now(), is_active=True)
    for job in expired:
        job.is_active = False
        job.save()
    
    return f"✅ {expired.count()} jobs deactivated"

@shared_task
def send_daily_summary():
    """إرسال ملخص يومي للمشرفين"""
    from graduates.models import Graduate
    from employers.models import Employer
    from jobs.models import Job, JobApplication
    
    total_graduates = Graduate.objects.filter(is_verified=True).count()
    total_employers = Employer.objects.filter(is_verified=True).count()
    total_jobs = Job.objects.filter(is_active=True).count()
    total_applications = JobApplication.objects.count()
    
    message = f"""
    📊 ملخص المنصة اليومي:
    - الخريجين: {total_graduates}
    - الشركات: {total_employers}
    - الوظائف النشطة: {total_jobs}
    - طلبات التوظيف: {total_applications}
    """
    
    # إرسال إشعار للمشرفين
    from dashboard.models import AdminProfile
    admins = AdminProfile.objects.filter(is_active=True)
    for admin in admins:
        Notification.objects.create(
            recipient=admin.user,
            title='📊 ملخص المنصة اليومي',
            message=message[:200],
            link='/dashboard/',
            notification_type='info'
        )
    
    return "✅ Daily summary sent"