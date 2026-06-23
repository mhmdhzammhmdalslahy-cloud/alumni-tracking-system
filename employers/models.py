# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User

class Employer(models.Model):
    INDUSTRY_CHOICES = [
        ('tech', 'تقنية المعلومات'),
        ('construction', 'مقاولات وإنشاءات'),
        ('medical', 'طبي وصحي'),
        ('education', 'تعليم وتدريب'),
        ('marketing', 'تسويق وإعلان'),
        ('finance', 'مالي ومصارف'),
        ('consulting', 'استشارات'),
        ('real_estate', 'عقارات'),
        ('transport', 'نقل وخدمات لوجستية'),
        ('hospitality', 'ضيافة وسياحة'),
        ('oil_gas', 'نفط وغاز'),
        ('telecom', 'اتصالات'),
        ('other', 'أخرى'),
    ]
    
    EMPLOYEE_CHOICES = [
        ('1-10', '1-10 موظف'),
        ('11-50', '11-50 موظف'),
        ('51-200', '51-200 موظف'),
        ('201-500', '201-500 موظف'),
        ('501-1000', '501-1000 موظف'),
        ('1000+', 'أكثر من 1000 موظف'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField("اسم الشركة", max_length=200, unique=True)
    short_name = models.CharField("الاسم المختصر", max_length=50, blank=True, null=True)
    industry = models.CharField("القطاع", max_length=50, choices=INDUSTRY_CHOICES)
    employee_count = models.CharField("عدد الموظفين", max_length=20, choices=EMPLOYEE_CHOICES, blank=True, null=True)
    founded_year = models.IntegerField("سنة التأسيس", null=True, blank=True)
    headquarters = models.CharField("المقر الرئيسي", max_length=200)
    about = models.TextField("نبذة عن الشركة")
    website = models.URLField("الموقع الإلكتروني", blank=True, null=True)
    logo = models.ImageField("شعار الشركة", upload_to='logos/', blank=True, null=True)
    cover_image = models.ImageField("صورة الغلاف", upload_to='covers/', blank=True, null=True)
    commercial_registration = models.CharField("السجل التجاري", max_length=50, unique=True, blank=True, null=True)
    tax_number = models.CharField("الرقم الضريبي", max_length=50, blank=True, null=True)
    phone = models.CharField("رقم الهاتف", max_length=20, blank=True, null=True)
    email = models.EmailField("البريد الإلكتروني للتواصل", blank=True, null=True)
    address = models.TextField("العنوان التفصيلي", blank=True, null=True)
    latitude = models.DecimalField("خط العرض", max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField("خط الطول", max_digits=9, decimal_places=6, null=True, blank=True)
    is_verified = models.BooleanField("حساب موثق", default=False)
    is_active = models.BooleanField("نشط", default=True)
    views_count = models.IntegerField("عدد المشاهدات", default=0)
    created_at = models.DateTimeField("تاريخ التسجيل", auto_now_add=True)
    updated_at = models.DateTimeField("آخر تحديث", auto_now=True)
    
    def __str__(self):
        return self.company_name
    
    def get_jobs_count(self):
        return self.jobs.filter(is_active=True).count()
    
    def get_applications_count(self):
        total = 0
        for job in self.jobs.all():
            total += job.applications.count()
        return total
    
    # ✅ هذه الدوال يجب أن تكون هنا (داخل نموذج Employer)
    @property
    def avg_rating(self):
        """حساب متوسط التقييم"""
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 0
    
    @property
    def reviews_count(self):
        return self.reviews.count()


class EmployerVerificationRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تم القبول'),
        ('rejected', 'مرفوض'),
    ]
    
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='verification_requests')
    commercial_registration_file = models.FileField("السجل التجاري", upload_to='verifications/')
    tax_certificate = models.FileField("شهادة الضريبة", upload_to='verifications/', blank=True, null=True)
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField("ملاحظات", blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reviewed_at = models.DateTimeField("تاريخ المراجعة", null=True, blank=True)
    created_at = models.DateTimeField("تاريخ الطلب", auto_now_add=True)
    
    def __str__(self):
        return f"{self.employer.company_name} - {self.status}"


# ✅ النموذج الصحيح لتقييم الشركة
class CompanyReview(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='reviews')
    graduate = models.ForeignKey('graduates.Graduate', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('employer', 'graduate')