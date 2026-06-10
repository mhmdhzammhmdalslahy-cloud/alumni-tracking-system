from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from graduates.models import Graduate
from employers.models import Employer
from jobs.models import Job
from dashboard.models import Notification, VerificationRequest, EmployerVerificationRequest

# 1. خريج جديد -> إشعار للإدارة (أول مشرف أو مستخدم staff)
@receiver(post_save, sender=Graduate)
def notify_new_graduate(sender, instance, created, **kwargs):
    if created:
        # إرسال إشعار لكل مشرف (admin_profile)
        from dashboard.models import AdminProfile
        admins = AdminProfile.objects.filter(is_active=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin.user,
                title="خريج جديد",
                message=f"تم تسجيل خريج جديد: {instance.user.get_full_name()} (تخصص {instance.major})",
                notification_type='info',
                link=f"/graduates/{instance.id}/"
            )

# 2. وظيفة جديدة -> إشعار للخريجين حسب التخصص
@receiver(post_save, sender=Job)
def notify_new_job(sender, instance, created, **kwargs):
    if created:
        # نبحث عن خريجين لديهم نفس التخصص (نص تقريبي)
        related_graduates = Graduate.objects.filter(major__icontains=instance.title)  # أو حسب وصف الوظيفة
        for grad in related_graduates:
            Notification.objects.create(
                recipient=grad.user,
                title="وظيفة جديدة",
                message=f"وظيفة {instance.title} في {instance.employer.company_name} مناسبة لك.",
                notification_type='success',
                link=f"/jobs/{instance.id}/"
            )
        # أيضاً إشعار للإدارة
        from dashboard.models import AdminProfile
        admins = AdminProfile.objects.filter(is_active=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin.user,
                title="وظيفة جديدة منشورة",
                message=f"تم نشر وظيفة {instance.title} بواسطة {instance.employer.company_name}",
                notification_type='info',
                link=f"/jobs/{instance.id}/"
            )

# 3. شركة جديدة -> إشعار للإدارة
@receiver(post_save, sender=Employer)
def notify_new_employer(sender, instance, created, **kwargs):
    if created:
        from dashboard.models import AdminProfile
        admins = AdminProfile.objects.filter(is_active=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin.user,
                title="شركة جديدة",
                message=f"تم تسجيل شركة جديدة: {instance.company_name} ({instance.industry})",
                notification_type='info',
                link=f"/employers/{instance.id}/"
            )

# 4. نتيجة التحقق (VerificationRequest) -> إشعار للخريج
@receiver(post_save, sender=VerificationRequest)
def notify_verification_result(sender, instance, **kwargs):
    if instance.status in ['approved', 'rejected'] and instance.reviewed_at:
        if instance.status == 'approved':
            title = "تم توثيق حسابك"
            msg = f"تم قبول طلب توثيق حساب الخريج الخاص بك. أصبحت موثقاً."
            notif_type = 'success'
        else:
            title = "تم رفض طلب التوثيق"
            msg = f"عذراً، تم رفض طلب توثيق حسابك. السبب: {instance.rejection_reason or 'غير محدد'}"
            notif_type = 'danger'
        Notification.objects.create(
            recipient=instance.graduate.user,
            title=title,
            message=msg,
            notification_type=notif_type,
            link="/profile/"  # أو رابط الملف الشخصي
        )

# 5. نتيجة التحقق للشركات (EmployerVerificationRequest) -> إشعار للشركة
@receiver(post_save, sender=EmployerVerificationRequest)
def notify_employer_verification(sender, instance, **kwargs):
    if instance.status in ['approved', 'rejected'] and instance.reviewed_at:
        if instance.status == 'approved':
            title = "تم توثيق حساب الشركة"
            msg = f"تم قبول طلب توثيق شركة {instance.employer.company_name}. يمكنكم الآن نشر الوظائف."
            notif_type = 'success'
        else:
            title = "تم رفض طلب توثيق الشركة"
            msg = f"عذراً، تم رفض طلب توثيق شركتكم. السبب: {instance.rejection_reason or 'غير محدد'}"
            notif_type = 'danger'
        Notification.objects.create(
            recipient=instance.employer.user,
            title=title,
            message=msg,
            notification_type=notif_type,
            link="/employer/profile/"
        )