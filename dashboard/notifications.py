from django.core.mail import send_mail
from django.conf import settings
from graduates.models import Graduate
from jobs.models import Job

def send_email_notification(recipient_email, subject, message):
    """إرسال بريد إلكتروني"""
    if recipient_email:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )

def notify_graduates_about_new_job(job):
    """إرسال إشعارات بريدية لجميع الخريجين بوظيفة جديدة"""
    graduates = Graduate.objects.filter(
        receive_email_notifications=True,
        user__is_active=True
    )
    subject = f"📢 وظيفة جديدة: {job.title}"
    message = f"""
مرحباً،

تم نشر وظيفة جديدة قد تهمك:
العنوان: {job.title}
الشركة: {job.employer.company_name}
الموقع: {job.location}
الراتب: {job.salary_min} - {job.salary_max}

للتفاصيل والتقديم: http://127.0.0.1:8000/jobs/{job.id}/

نتمنى لك التوفيق،
فريق متابعة الخريجين
"""

    for grad in graduates:
        if grad.user.email:
            send_email_notification(grad.user.email, subject, message)