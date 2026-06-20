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
    
    # ✅ حقل جديد للردود المتداخلة (التعليق على تعليق)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name="التعليق الأصلي"
    )
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"تعليق من {self.created_by.username} على {self.topic.title}"


# ========== نماذج غرف المكالمات (Call Rooms) ==========

class CallRoom(models.Model):
    ROOM_TYPES = [
        ('video', '🎥 مكالمة فيديو'),
        ('audio', '🎧 مكالمة صوتية'),
        ('live', '📺 بث مباشر'),
    ]
    
    STATUS_CHOICES = [
        ('waiting', 'في انتظار المشاركين'),
        ('active', 'جارية'),
        ('ended', 'انتهت'),
    ]
    
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='call_rooms')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    room_name = models.CharField(max_length=100)
    room_type = models.CharField("نوع الغرفة", max_length=20, choices=ROOM_TYPES, default='video')
    status = models.CharField("الحالة", max_length=20, choices=STATUS_CHOICES, default='waiting')
    participants = models.ManyToManyField(User, related_name='joined_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    likes = models.IntegerField("الإعجابات", default=0)
    
    def __str__(self):
        return f"{self.room_name} ({self.get_status_display()})"
    
    def participant_count(self):
        return self.participants.count()
    
    def is_active(self):
        return self.status == 'active'
    
    def get_room_type_display_icon(self):
        icons = {
            'video': '🎥',
            'audio': '🎧',
            'live': '📺'
        }
        return icons.get(self.room_type, '📹')


class RoomParticipant(models.Model):
    room = models.ForeignKey(CallRoom, on_delete=models.CASCADE, related_name='participants_detail')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_muted = models.BooleanField(default=False)
    is_video_off = models.BooleanField(default=False)
    is_online = models.BooleanField("متصل", default=True)
    is_creator = models.BooleanField("منشئ الغرفة", default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    peer_id = models.CharField("Peer ID", max_length=100, null=True, blank=True)
    
    class Meta:
        unique_together = ('room', 'user')
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} في {self.room.room_name}"