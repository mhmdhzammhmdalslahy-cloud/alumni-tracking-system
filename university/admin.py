from django.contrib import admin
from .models import (
    UniversityNews,
    StudyMaterial,
    Job,
    Course,
    Partner,
    AcademicCalendar
)

# ============================================================
# 1. الأخبار والإعلانات
# ============================================================
@admin.register(UniversityNews)
class UniversityNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'published_at', 'created_by']
    list_filter = ['category', 'is_published']
    search_fields = ['title', 'content']
    ordering = ['-published_at']
    date_hierarchy = 'published_at'
    readonly_fields = ['published_at']
    
    fieldsets = (
        ('المحتوى', {
            'fields': ('title', 'content', 'category', 'image')
        }),
        ('النشر', {
            'fields': ('is_published', 'link', 'created_by')
        }),
        ('التواريخ', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# ============================================================
# 2. المواد الدراسية (المكتبة الرقمية)
# ============================================================
@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'created_at', 'uploaded_by']
    list_filter = ['category']
    search_fields = ['title', 'description']
    ordering = ['-created_at']

# ============================================================
# 3. الوظائف (مركز التوظيف)
# ============================================================
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'job_type', 'location', 'is_active', 'deadline']
    list_filter = ['job_type', 'is_active']
    search_fields = ['title', 'company', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

# ============================================================
# 4. الدورات (التعليم المستمر)
# ============================================================
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'is_active', 'start_date']
    list_filter = ['level', 'is_active']
    search_fields = ['title', 'instructor', 'description']
    ordering = ['-created_at']

# ============================================================
# 5. الشركاء
# ============================================================
@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['name', 'website', 'order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

# ============================================================
# 6. التقويم الأكاديمي
# ============================================================
@admin.register(AcademicCalendar)
class AcademicCalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'is_holiday', 'is_active']
    list_filter = ['is_holiday', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['date']
    date_hierarchy = 'date'