from django.db import models
from django.contrib.auth.models import User
from graduates.models import Graduate

class Group(models.Model):
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبولة'),
        ('rejected', 'مرفوضة'),
    ]
    
    name = models.CharField("اسم المجموعة", max_length=100, unique=True)
    description = models.TextField("وصف المجموعة", blank=True)
    category = models.CharField("الفئة", max_length=50, blank=True, help_text="مثال: تخصص, سنة تخرج, مجال وظيفي")
    image = models.ImageField("صورة الغلاف", upload_to='groups/', blank=True, null=True)
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default='pending')
    members = models.ManyToManyField(Graduate, related_name='joined_groups', blank=True, verbose_name="الأعضاء")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def member_count(self):
        return self.members.count()


class Topic(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField("الموضوع", max_length=200)
    content = models.TextField("المحتوى")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_topics')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def comment_count(self):
        return self.comments.count()


class Comment(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField("التعليق")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_comments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"تعليق من {self.created_by.username} على {self.topic.title}"