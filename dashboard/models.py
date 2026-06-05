from django.db import models
from django.contrib.auth.models import User

class AdminProfile(models.Model):
    ADMIN_LEVELS = [
        ('super_admin', 'مدير النظام'),
        ('alumni_manager', 'مدير شؤون الخريجين'),
        ('academic_admin', 'مشرف أكاديمي'),
        ('content_moderator', 'مشرف محتوى'),
        ('report_viewer', 'مدير تقارير'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    admin_level = models.CharField("مستوى المشرف", max_length=30, choices=ADMIN_LEVELS)
    permissions = models.JSONField("صلاحيات إضافية", default=dict)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_admins')
    is_active = models.BooleanField("نشط", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_admin_level_display()}"


class VerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تم القبول'),
        ('rejected', 'مرفوض'),
    ]
    
    graduate = models.ForeignKey('graduates.Graduate', on_delete=models.CASCADE, related_name='verification_requests')
    student_university_number = models.CharField("الرقم الجامعي", max_length=20)
    uploaded_document = models.FileField("الوثيقة المرفقة", upload_to='verifications/graduates/')
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField("تاريخ المراجعة", null=True, blank=True)
    rejection_reason = models.TextField("سبب الرفض", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.graduate.user.get_full_name()} - {self.status}"


class EmployerVerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تم القبول'),
        ('rejected', 'مرفوض'),
    ]
    
    employer = models.ForeignKey('employers.Employer', on_delete=models.CASCADE, related_name='admin_verification_requests')
    commercial_registration_file = models.FileField("السجل التجاري", upload_to='verifications/employers/')
    tax_certificate = models.FileField("شهادة الضريبة", upload_to='verifications/employers/', blank=True, null=True)
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField("تاريخ المراجعة", null=True, blank=True)
    rejection_reason = models.TextField("سبب الرفض", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employer.company_name} - {self.status}"


class Survey(models.Model):
    TIMING_CHOICES = [
        ('upon_graduation', 'عند التخرج'),
        ('after_6_months', 'بعد 6 أشهر'),
        ('after_12_months', 'بعد 12 شهر'),
        ('after_18_months', 'بعد 18 شهر'),
    ]
    
    title = models.CharField("عنوان الاستبيان", max_length=200)
    timing = models.CharField("التوقيت", max_length=30, choices=TIMING_CHOICES)
    questions = models.JSONField("الأسئلة")
    scheduled_date = models.DateTimeField("تاريخ الإرسال المجدول", null=True, blank=True)
    is_active = models.BooleanField("نشط", default=True)
    created_by = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    graduate = models.ForeignKey('graduates.Graduate', on_delete=models.CASCADE)
    answers = models.JSONField("الإجابات")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('survey', 'graduate')
    
    def __str__(self):
        return f"{self.graduate.user.get_full_name()} - {self.survey.title}"


class Event(models.Model):
    EVENT_TYPES = [
        ('job_fair', 'ملتقى توظيف'),
        ('workshop', 'ورشة عمل'),
        ('seminar', 'ندوة'),
        ('graduation', 'حفل تخرج'),
        ('training', 'دورة تدريبية'),
    ]
    
    title = models.CharField("عنوان الفعالية", max_length=200)
    event_type = models.CharField("نوع الفعالية", max_length=30, choices=EVENT_TYPES)
    description = models.TextField("الوصف")
    date = models.DateTimeField("تاريخ الفعالية")
    location = models.CharField("الموقع", max_length=200)
    is_virtual = models.BooleanField("افتراضية", default=False)
    meeting_link = models.URLField("رابط الفعالية الافتراضية", blank=True, null=True)
    max_attendees = models.IntegerField("الحد الأقصى للحضور", null=True, blank=True)
    image = models.ImageField("صورة الفعالية", upload_to='events/', blank=True, null=True)
    is_active = models.BooleanField("نشطة", default=True)
    created_by = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class EventAttendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    graduate = models.ForeignKey('graduates.Graduate', on_delete=models.CASCADE)
    attended = models.BooleanField("حضر", default=False)
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('event', 'graduate')
    
    def __str__(self):
        return f"{self.graduate.user.get_full_name()} - {self.event.title}"


class Report(models.Model):
    REPORT_TYPES = [
        ('employment', 'تقرير التوظيف'),
        ('skill_gap', 'تقرير فجوات المهارات'),
        ('satisfaction', 'تقرير رضا الخريجين'),
        ('survey_performance', 'تقرير أداء الاستبيانات'),
        ('company_activity', 'تقرير نشاط الشركات'),
        ('system_health', 'تقرير سير النظام'),
    ]
    
    report_name = models.CharField("اسم التقرير", max_length=200)
    report_type = models.CharField("نوع التقرير", max_length=30, choices=REPORT_TYPES)
    parameters = models.JSONField("معاملات التقرير", default=dict)
    file_path = models.FileField("ملف التقرير", upload_to='reports/', blank=True, null=True)
    generated_by = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    is_scheduled = models.BooleanField("مجدول", default=False)
    scheduled_recipient = models.EmailField("البريد المستلم للتقرير المجدول", blank=True, null=True)
    
    def __str__(self):
        return self.report_name


class SystemSetting(models.Model):
    SETTING_TYPES = [
        ('general', 'إعدادات عامة'),
        ('registration', 'إعدادات التسجيل'),
        ('verification', 'إعدادات التوثيق'),
        ('notification', 'إعدادات الإشعارات'),
        ('privacy', 'إعدادات الخصوصية'),
    ]
    
    setting_type = models.CharField("نوع الإعداد", max_length=30, choices=SETTING_TYPES)
    key = models.CharField("المفتاح", max_length=100, unique=True)
    value = models.TextField("القيمة")
    description = models.TextField("الوصف", blank=True, null=True)
    updated_by = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.key}: {self.value}"


class AuditLog(models.Model):
    ACTION_TYPES = [
        ('create', 'إنشاء'),
        ('update', 'تحديث'),
        ('delete', 'حذف'),
        ('approve', 'موافقة'),
        ('reject', 'رفض'),
        ('login', 'تسجيل دخول'),
        ('logout', 'تسجيل خروج'),
        ('export', 'تصدير'),
    ]
    
    admin = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True)
    action = models.CharField("الإجراء", max_length=30, choices=ACTION_TYPES)
    target_type = models.CharField("نوع المستهدف", max_length=50)
    target_id = models.IntegerField("معرف المستهدف", null=True, blank=True)
    details = models.JSONField("تفاصيل إضافية", default=dict)
    ip_address = models.GenericIPAddressField("عنوان IP", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.admin} - {self.action} - {self.target_type} at {self.created_at}"


class Major(models.Model):
    name = models.CharField("اسم التخصص", max_length=100, unique=True)
    code = models.CharField("رمز التخصص", max_length=20, unique=True)
    department = models.CharField("القسم", max_length=100)
    is_active = models.BooleanField("نشط", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField("اسم المهارة", max_length=100, unique=True)
    category = models.CharField("التصنيف", max_length=50, blank=True, null=True)
    is_active = models.BooleanField("نشط", default=True)
    
    def __str__(self):
        return self.name


class BannedWord(models.Model):
    word = models.CharField("الكلمة", max_length=100, unique=True)
    created_by = models.ForeignKey(AdminProfile, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.word
class SuccessStory(models.Model):
    graduate = models.ForeignKey('graduates.Graduate', on_delete=models.CASCADE, related_name='success_stories')
    title = models.CharField("العنوان", max_length=200)
    content = models.TextField("المحتوى")
    image = models.ImageField("الصورة", upload_to='success_stories/', blank=True, null=True)
    is_active = models.BooleanField("نشط", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title