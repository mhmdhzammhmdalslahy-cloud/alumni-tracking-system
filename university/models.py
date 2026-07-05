from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# ============================================================
# 1. المحتوى الرئيسي (أخبار - إعلانات - فعاليات)
# ============================================================
class UniversityNews(models.Model):
    CATEGORY_CHOICES = [
        ('announcement', '📢 إعلان'),
        ('event', '📅 فعالية'),
        ('achievement', '🏆 إنجاز'),
        ('general', '📰 خبر عام'),
        ('job', '💼 وظيفة'),  # للوظائف المميزة التي تظهر في الأخبار
    ]
    
    title = models.CharField("العنوان", max_length=200)
    content = models.TextField("المحتوى")
    category = models.CharField("التصنيف", max_length=20, choices=CATEGORY_CHOICES, default='general')
    image = models.ImageField("صورة", upload_to='university/news/', blank=True, null=True)
    is_published = models.BooleanField("منشور", default=True)
    published_at = models.DateTimeField("تاريخ النشر", auto_now_add=True)
    link = models.URLField("رابط خارجي", blank=True, null=True)  # للوظائف أو التسجيل
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_news')
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
    
    class Meta:
        ordering = ['-published_at']
        verbose_name = "خبر/إعلان"
        verbose_name_plural = "الأخبار والإعلانات"

# ============================================================
# 2. الوظائف (مركز التوظيف)
# ============================================================
class Job(models.Model):
    JOB_TYPES = [
        ('full_time', 'دوام كامل'),
        ('part_time', 'دوام جزئي'),
        ('remote', 'عن بعد'),
        ('internship', 'تدريب'),
    ]
    
    title = models.CharField("عنوان الوظيفة", max_length=200)
    company = models.CharField("الشركة", max_length=200)
    description = models.TextField("وصف الوظيفة")
    requirements = models.TextField("المتطلبات", blank=True)
    job_type = models.CharField("نوع الوظيفة", max_length=20, choices=JOB_TYPES, default='full_time')
    location = models.CharField("الموقع", max_length=200, blank=True)
    salary = models.CharField("الراتب", max_length=100, blank=True)
    is_active = models.BooleanField("نشطة", default=True)
    deadline = models.DateTimeField("آخر موعد للتقديم", null=True, blank=True)
    created_at = models.DateTimeField("تاريخ النشر", auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_jobs')
    
    def __str__(self):
        return f"{self.title} - {self.company}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "وظيفة"
        verbose_name_plural = "الوظائف"

# ============================================================
# 3. الدورات (التعليم المستمر)
# ============================================================
class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'مبتدئ'),
        ('intermediate', 'متوسط'),
        ('advanced', 'متقدم'),
    ]
    
    title = models.CharField("عنوان الدورة", max_length=200)
    instructor = models.CharField("المدرب", max_length=200, blank=True)
    description = models.TextField("وصف الدورة")
    level = models.CharField("المستوى", max_length=20, choices=LEVEL_CHOICES, default='beginner')
    start_date = models.DateField("تاريخ البداية", null=True, blank=True)
    duration = models.CharField("المدة", max_length=100, blank=True)  # مثلاً: "4 أسابيع"
    is_active = models.BooleanField("متاحة", default=True)
    image = models.ImageField("صورة", upload_to='courses/', blank=True, null=True)
    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "دورة"
        verbose_name_plural = "الدورات"

# ============================================================
# 4. المكتبة الرقمية (مواد دراسية)
# ============================================================
class StudyMaterial(models.Model):
    CATEGORY_CHOICES = [
        ('pdf', 'PDF'),
        ('video', 'فيديو'),
        ('doc', 'مستند'),
        ('link', 'رابط خارجي'),
    ]
    
    title = models.CharField("العنوان", max_length=200)
    description = models.TextField("الوصف", blank=True)
    category = models.CharField("النوع", max_length=20, choices=CATEGORY_CHOICES, default='pdf')
    file = models.FileField("الملف", upload_to='study/', blank=True, null=True)
    link = models.URLField("رابط", blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField("تاريخ الإضافة", auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "مادة دراسية"
        verbose_name_plural = "المواد الدراسية"

# ============================================================
# 5. الشركاء (الأيقونة الجانبية)
# ============================================================
class Partner(models.Model):
    name = models.CharField("اسم الشريك", max_length=200)
    logo = models.ImageField("الشعار", upload_to='partners/', blank=True, null=True)
    website = models.URLField("الموقع الإلكتروني", blank=True)
    description = models.TextField("وصف", blank=True)
    order = models.IntegerField("ترتيب العرض", default=0)
    is_active = models.BooleanField("نشط", default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "شريك"
        verbose_name_plural = "الشركاء"

# ============================================================
# 6. التقويم الأكاديمي
# ============================================================
class AcademicCalendar(models.Model):
    title = models.CharField("العنوان", max_length=200)
    date = models.DateField("التاريخ")
    description = models.TextField("الوصف", blank=True)
    is_holiday = models.BooleanField("إجازة رسمية", default=False)
    is_active = models.BooleanField("نشط", default=True)
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    class Meta:
        ordering = ['date']
        verbose_name = "حدث تقويمي"
        verbose_name_plural = "التقويم الأكاديمي"