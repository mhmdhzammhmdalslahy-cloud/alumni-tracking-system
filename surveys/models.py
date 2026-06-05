from django.db import models
from django.contrib.auth.models import User

class Survey(models.Model):
    TIMING_CHOICES = [
        ('upon_graduation', 'عند التخرج'),
        ('after_6_months', 'بعد 6 أشهر'),
        ('after_12_months', 'بعد 12 شهر'),
        ('after_18_months', 'بعد 18 شهر'),
    ]
    
    title = models.CharField("عنوان الاستبيان", max_length=200)
    description = models.TextField("الوصف", blank=True, null=True)
    timing = models.CharField("التوقيت", max_length=30, choices=TIMING_CHOICES)
    questions = models.JSONField("الأسئلة")
    is_active = models.BooleanField("نشط", default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def get_response_count(self):
        return self.responses.count()


class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    graduate = models.ForeignKey('graduates.Graduate', on_delete=models.CASCADE, related_name='survey_responses')
    answers = models.JSONField("الإجابات")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('survey', 'graduate')
    
    def __str__(self):
        return f"{self.graduate.user.get_full_name()} - {self.survey.title}"