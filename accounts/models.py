from django.db import models
from django.contrib.auth.models import User

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"