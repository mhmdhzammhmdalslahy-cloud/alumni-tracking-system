from django.db import models

from django.core.validators import RegexValidator

# ============================================================
# ✅ Validators مركزية لجميع الحقول
# ============================================================
letters_validator = RegexValidator(
    r'^[\u0621-\u064A\u0660-\u0669a-zA-Z\s]+$',
    'يسمح بالحروف فقط'
)
numbers_validator = RegexValidator(
    r'^\d+$',
    'يسمح بالأرقام فقط'
)
both_validator = RegexValidator(
    r'^[\u0621-\u064A\u0660-\u0669a-zA-Z0-9\s]+$',
    'يسمح بالحروف والأرقام فقط'
)
phone_validator = RegexValidator(
    r'^(0|7|9)\d{8,9}$',
    'رقم الهاتف يجب أن يبدأ بـ 0 أو 7 أو 9'
)
university_validator = RegexValidator(
    r'^\d+$',
    'الرقم الجامعي أرقام فقط'
)

from django.contrib.auth.models import User
from django.utils import timezone
import secrets
from datetime import timedelta


class NormalUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_normal_profile')
    phone = models.CharField("رقم الجوال", max_length=15)
    is_graduate = models.BooleanField("هل هو خريج؟", default=False)
    is_employer = models.BooleanField("هل هو شركة؟", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account_profile')
    phone = models.CharField("رقم الجوال", max_length=15, blank=True, null=True)
    address = models.TextField("العنوان", blank=True, null=True)
    profile_picture = models.ImageField("الصورة الشخصية", upload_to='profiles/', blank=True, null=True)
    is_email_verified = models.BooleanField("تم تأكيد البريد الإلكتروني", default=False)  # ✅ إضافة حقل التحقق
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


# ============================================================
# ✅ نموذج التحقق عبر البريد الإلكتروني (Email Verification)
# ============================================================
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_verification')
    code = models.CharField("رمز التأكيد", max_length=6)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    is_verified = models.BooleanField("تم التحقق", default=False)
    attempts = models.IntegerField("عدد محاولات الفشل", default=0)  # ✅ لحماية من محاولات متكررة

    class Meta:
        verbose_name = "التحقق من البريد الإلكتروني"
        verbose_name_plural = "التحقق من البريد الإلكتروني"
        ordering = ['-created_at']

    def is_expired(self):
        """التحقق من انتهاء صلاحية الرمز (10 دقائق)"""
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def generate_code(self):
        """توليد رمز عشوائي من 6 أرقام"""
        self.code = f"{secrets.randbelow(1000000):06d}"
        self.created_at = timezone.now()
        self.attempts = 0
        self.save()
        return self.code

    def increment_attempts(self):
        """زيادة عدد محاولات الفشل"""
        self.attempts += 1
        self.save()
        return self.attempts

    def is_blocked(self):
        """التحقق إذا كان المستخدم محظوراً بسبب كثرة المحاولات (أكثر من 5 محاولات)"""
        return self.attempts >= 5

    def __str__(self):
        return f"{self.user.username} - {self.code} - {'✅ تم التحقق' if self.is_verified else '⏳ قيد الانتظار'}"