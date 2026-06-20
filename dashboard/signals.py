from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from graduates.models import Graduate
from django.dispatch import receiver
from jobs.models import Job
from dashboard.notifications import notify_graduates_about_new_job
from employers.models import Employer
from jobs.models import Job
from dashboard.models import Notification, VerificationRequest, EmployerVerificationRequest, AdminProfile

# 1. خريج جديد -> إشعار للإدارة + ترحيب للخريج
@receiver(post_save, sender=Graduate)
def notify_new_graduate(sender, instance, created, **kwargs):
    if created:
        # إشعار ترحيبي للخريج نفسه
        Notification.objects.create(
            recipient=instance.user,
            title="🎓 مرحباً بك في نظام متابعة الخريجين",
            message=f"أهلاً {instance.user.get_full_name()}، تم تسجيلك بنجاح. يمكنك الآن إكمال ملفك الشخصي والتقدم للوظائف.",
            notification_type='welcome',
            link=f"/graduates/{instance.id}/"
        )
        # إشعار للإدارة (جميع المشرفين النشطين)
        admins = AdminProfile.objects.filter(is_active=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin.user,
                title="📢 خريج جديد",
                message=f"تم تسجيل خريج جديد: {instance.user.get_full_name()} - تخصص {instance.major}.",
                notification_type='info',
                link=f"/dashboard/graduates/{instance.id}/verify/"
            )

# 2. وظيفة جديدة -> إشعار للخريجين بناءً على تخصصهم أو المهارات
@receiver(post_save, sender=Job)
def notify_new_job(sender, instance, created, **kwargs):
    if created:
        # البحث عن خريجين لديهم نفس التخصص (أو تخصص قريب)
        related_graduates = Graduate.objects.filter(major__icontains=instance.title.split()[0] if instance.title else '')
        # بديل: يمكن البحث في مهارات الخريجين (يتطلب علاقة ManyToMany)
        # إذا لم نجد أحداً، نرسل لآخر 10 خريجين نشطين
        if not related_graduates.exists():
            related_graduates = Graduate.objects.all().order_by('-created_at')[:10]
        
        for grad in related_graduates:
            Notification.objects.create(
                recipient=grad.user,
                title="💼 وظيفة جديدة مناسبة لك",
                message=f"وظيفة {instance.title} في شركة {instance.employer.company_name} - قد تناسب ملفك المهني.",
                notification_type='new_job',
                link=f"/jobs/{instance.id}/"
            )
        # إشعار للإدارة
        admins = AdminProfile.objects.filter(is_active=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin.user,
                title="📌 وظيفة جديدة منشورة",
                message=f"تم نشر وظيفة {instance.title} بواسطة {instance.employer.company_name}.",
                notification_type='info',
                link=f"/dashboard/jobs/"
            )

# 3. شركة جديدة -> إشعار للإدارة
@receiver(post_save, sender=Employer)
def notify_new_employer(sender, instance, created, **kwargs):
    if created:
        admins = AdminProfile.objects.filter(is_active=True)
        for admin in admins:
            Notification.objects.create(
                recipient=admin.user,
                title="🏢 شركة جديدة",
                message=f"تم تسجيل شركة جديدة: {instance.company_name} - القطاع: {instance.industry}.",
                notification_type='info',
                link=f"/dashboard/employers/{instance.id}/verify/"
            )

# 4. نتيجة التحقق للخريج -> إشعار للخريج
@receiver(post_save, sender=VerificationRequest)
def notify_verification_result(sender, instance, **kwargs):
    if instance.status in ['approved', 'rejected'] and instance.reviewed_at:
        if instance.status == 'approved':
            title = "✅ تم توثيق حسابك"
            msg = "تم قبول طلب توثيق حساب الخريج الخاص بك. أصبحت موثقاً الآن."
            notif_type = 'verification_approved'
            link = f"/graduates/{instance.graduate.id}/"
        else:
            title = "❌ تم رفض طلب التوثيق"
            msg = f"عذراً، تم رفض طلب توثيق حسابك. السبب: {instance.rejection_reason or 'غير محدد'}"
            notif_type = 'verification_rejected'
            link = "/profile/"
        Notification.objects.create(
            recipient=instance.graduate.user,
            title=title,
            message=msg,
            notification_type=notif_type,
            link=link
        )

# 5. نتيجة التحقق للشركة -> إشعار للشركة
@receiver(post_save, sender=EmployerVerificationRequest)
def notify_employer_verification(sender, instance, **kwargs):
    if instance.status in ['approved', 'rejected'] and instance.reviewed_at:
        if instance.status == 'approved':
            title = "✅ تم توثيق حساب الشركة"
            msg = f"تم قبول طلب توثيق شركة {instance.employer.company_name}. يمكنكم الآن نشر الوظائف."
            notif_type = 'verification_approved'
            link = f"/employers/{instance.employer.id}/"
        else:
            title = "❌ تم رفض طلب توثيق الشركة"
            msg = f"عذراً، تم رفض طلب توثيق شركتكم. السبب: {instance.rejection_reason or 'غير محدد'}"
            notif_type = 'verification_rejected'
            link = "/employer/profile/"
        Notification.objects.create(
            recipient=instance.employer.user,
            title=title,
            message=msg,
            notification_type=notif_type,
            link=link
        )

        
@receiver(post_save, sender=Job)
def send_job_notifications(sender, instance, created, **kwargs):
    if created and instance.is_active:
        notify_graduates_about_new_job(instance)