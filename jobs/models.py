from django.db import models
from employers.models import Employer
from graduates.models import Graduate

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'دوام كامل'),
        ('part_time', 'دوام جزئي'),
        ('remote', 'عن بعد'),
        ('hybrid', 'هجين (حضوري وعن بعد)'),
        ('internship', 'تدريب'),
        ('contract', 'عقد مؤقت'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'مبتدئ (0-2 سنوات)'),
        ('junior', 'Junior (2-4 سنوات)'),
        ('mid', 'متوسط (4-7 سنوات)'),
        ('senior', 'Senior (7-10 سنوات)'),
        ('expert', 'خبير (10+ سنوات)'),
    ]
    
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField("المسمى الوظيفي", max_length=200)
    job_type = models.CharField("نوع الوظيفة", max_length=20, choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField("مستوى الخبرة", max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    location = models.CharField("الموقع", max_length=200)
    salary_min = models.DecimalField("الحد الأدنى للراتب", max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField("الحد الأقصى للراتب", max_digits=10, decimal_places=2, null=True, blank=True)
    is_salary_negotiable = models.BooleanField("الراتب قابل للتفاوض", default=False)
    required_skills = models.TextField("المهارات المطلوبة")
    preferred_skills = models.TextField("المهارات المفضلة", blank=True, null=True)
    description = models.TextField("الوصف الوظيفي")
    responsibilities = models.TextField("المسؤوليات", blank=True, null=True)
    benefits = models.TextField("المزايا", blank=True, null=True)
    deadline = models.DateField("آخر موعد للتقديم")
    is_active = models.BooleanField("نشطة", default=True)
    is_filled = models.BooleanField("تم شغلها", default=False)
    views_count = models.IntegerField("عدد المشاهدات", default=0)
    created_at = models.DateTimeField("تاريخ النشر", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    
    # ✅ الحقول الجديدة للبث المباشر
    is_live = models.BooleanField("بث مباشر", default=False)
    live_link = models.URLField("رابط البث المباشر", blank=True, null=True)
    
    def __str__(self):
        return f"{self.title} at {self.employer.company_name}"
    
    def get_applications_count(self):
        return self.applications.count()


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('reviewed', 'تمت المراجعة'),
        ('interview', 'مقابلة'),
        ('accepted', 'قبول مبدئي'),
        ('rejected', 'رفض'),
        ('hired', 'تم التعيين'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    graduate = models.ForeignKey(Graduate, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField("رسالة تعريفية", blank=True, null=True)
    expected_salary = models.DecimalField("الراتب المتوقع", max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField("ملاحظات صاحب العمل", blank=True, null=True)
    interview_date = models.DateTimeField("تاريخ المقابلة", null=True, blank=True)
    applied_at = models.DateTimeField("تاريخ التقديم", auto_now_add=True)
    reviewed_at = models.DateTimeField("تاريخ المراجعة", null=True, blank=True)
    
    class Meta:
        unique_together = ('job', 'graduate')
    
    def __str__(self):
        return f"{self.graduate} applied for {self.job.title}"