from django.db import models

class FAQ(models.Model):
    question = models.CharField("السؤال", max_length=200)
    answer = models.TextField("الإجابة")
    keywords = models.CharField("كلمات مفتاحية", max_length=200, blank=True, help_text="مفصولة بفاصلة")

    def __str__(self):
        return self.question