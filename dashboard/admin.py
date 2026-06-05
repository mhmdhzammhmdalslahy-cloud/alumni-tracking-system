 
from django.contrib import admin
from .models import AdminProfile, VerificationRequest, EmployerVerificationRequest, Survey, SurveyResponse, Event, EventAttendance, Report, SystemSetting, AuditLog, Major, Skill, BannedWord

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'admin_level', 'is_active', 'created_at']
    list_filter = ['admin_level', 'is_active']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']

@admin.register(VerificationRequest)
class VerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['graduate', 'student_university_number', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['graduate__user__first_name', 'student_university_number']

@admin.register(EmployerVerificationRequest)
class EmployerVerificationRequestAdmin(admin.ModelAdmin):
    list_display = ['employer', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['employer__company_name']

@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'timing', 'is_active', 'created_at']
    list_filter = ['timing', 'is_active']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'is_active']
    list_filter = ['event_type', 'is_active', 'is_virtual']

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['report_name', 'report_type', 'generated_at']
    list_filter = ['report_type']

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'setting_type', 'updated_at']
    list_filter = ['setting_type']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['admin', 'action', 'target_type', 'created_at']
    list_filter = ['action', 'target_type']
    readonly_fields = ['created_at']

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'is_active']
    list_filter = ['is_active', 'department']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(BannedWord)
class BannedWordAdmin(admin.ModelAdmin):
    list_display = ['word', 'created_at']
    search_fields = ['word']