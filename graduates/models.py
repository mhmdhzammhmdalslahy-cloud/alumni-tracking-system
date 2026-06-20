from django.db import models
from django.contrib.auth.models import User

class Graduate(models.Model):
    JOB_STATUS_CHOICES = [
        ('working', 'يعمل'),
        ('seeking', 'يبحث عن عمل'),
        ('studying', 'طالب دراسات عليا'),
        ('intern', 'متدرب'),
        ('entrepreneur', 'رائد أعمال'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='graduate_profile')
    university_id = models.CharField("الرقم الجامعي", max_length=20, unique=True)
    graduation_year = models.IntegerField("سنة التخرج")
    gpa = models.DecimalField("المعدل التراكمي", max_digits=5, decimal_places=2, null=True, blank=True)
    major = models.CharField("التخصص", max_length=100)
    minor = models.CharField("التخصص الفرعي", max_length=100, blank=True, null=True)
    bio = models.TextField("نبذة تعريفية", blank=True, null=True)
    current_job_status = models.CharField("الحالة الوظيفية", max_length=20, choices=JOB_STATUS_CHOICES, default='seeking')
    current_job_title = models.CharField("المسمى الوظيفي الحالي", max_length=100, blank=True, null=True)
    current_company = models.CharField("الشركة الحالية", max_length=100, blank=True, null=True)
    cv_file = models.FileField("السيرة الذاتية", upload_to='cvs/', blank=True, null=True)
    profile_picture = models.ImageField("الصورة الشخصية", upload_to='profiles/', blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    phone = models.CharField("رقم الجوال", max_length=15, blank=True, null=True)
    address = models.TextField("العنوان", blank=True, null=True)
    is_verified = models.BooleanField("حساب موثق", default=False)
    profile_views = models.IntegerField("عدد المشاهدات", default=0)
    reward_points = models.IntegerField("نقاط الحوافز", default=0)
    created_at = models.DateTimeField("تاريخ التسجيل", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    is_active = models.BooleanField(default=False)  # الخريج يبدأ غير نشط

    # ✅ حقل الإشعارات الجديد
    receive_email_notifications = models.BooleanField(
        default=True,
        verbose_name="استقبال إشعارات البريد الإلكتروني"
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class WorkExperience(models.Model):
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='work_experiences')
    job_title = models.CharField("المسمى الوظيفي", max_length=100)
    company = models.CharField("اسم الشركة", max_length=100)
    start_date = models.DateField("تاريخ البداية")
    end_date = models.DateField("تاريخ النهاية", null=True, blank=True)
    is_current = models.BooleanField("هل ما زلت تعمل هنا؟", default=False)
    description = models.TextField("وصف المهام", blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)  # حقل الهاتف (اختياري)

    def __str__(self):
        return f"{self.job_title} at {self.company}"


class Skill(models.Model):
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField("اسم المهارة", max_length=50)
    
    def __str__(self):
        return self.name


class Certification(models.Model):
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField("اسم الشهادة", max_length=100)
    issuing_organization = models.CharField("جهة الإصدار", max_length=100)
    issue_date = models.DateField("تاريخ الإصدار")
    expiry_date = models.DateField("تاريخ الانتهاء", null=True, blank=True)
    credential_url = models.URLField("رابط الشهادة", blank=True, null=True)
    
    def __str__(self):
        return self.name


class AcademicProject(models.Model):
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='academic_projects')
    name = models.CharField("اسم المشروع", max_length=100)
    description = models.TextField("وصف المشروع")
    year = models.IntegerField("السنة")
    project_url = models.URLField("رابط المشروع", blank=True, null=True)
    
    def __str__(self):
        return self.name


class ProfileViewLog(models.Model):
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='profile_views_log')
    viewer_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    viewer_ip = models.GenericIPAddressField("IP الزائر", null=True, blank=True)
    viewed_at = models.DateTimeField("تاريخ المشاهدة", auto_now_add=True)
    
    def __str__(self):
        return f"Viewed by {self.viewer_user or self.viewer_ip} at {self.viewed_at}"