from django.urls import path, include
from . import views

app_name = 'dashboard'

urlpatterns = [
    # ====== الصفحة الرئيسية ======
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # ====== إدارة الخريجين ======
    path('graduates/', views.manage_graduates, name='manage_graduates'),
    path('graduates/<int:pk>/verify/', views.verify_graduate, name='verify_graduate'),
    
    # ====== إدارة الشركات ======
    path('employers/', views.manage_employers, name='manage_employers'),
    path('employers/<int:pk>/verify/', views.verify_employer, name='verify_employer'),
    
    # ====== إدارة الاستبيانات ======
    path('surveys/', views.manage_surveys, name='manage_surveys'),
    path('surveys/create/', views.create_survey, name='create_survey'),
    path('surveys/<int:pk>/edit/', views.edit_survey, name='edit_survey'),
    path('surveys/<int:pk>/delete/', views.delete_survey, name='delete_survey'),
    path('survey/<int:survey_id>/publish/', views.publish_survey, name='publish_survey'),
    
    # ====== إدارة الفعاليات ======
    path('events/', views.manage_events, name='manage_events'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:pk>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:pk>/delete/', views.delete_event, name='delete_event'),
    
    # ====== التقارير ======
    path('reports/', views.reports, name='reports'),
    path('reports/generate/', views.generate_report, name='generate_report'),
    
    # ====== إعدادات النظام ======
    path('settings/', views.system_settings, name='system_settings'),
    
    # ====== إدارة المشرفين ======
    path('admins/', views.manage_admins, name='manage_admins'),
    path('admins/add/', views.add_admin, name='add_admin'),
    path('admins/<int:pk>/edit/', views.edit_admin, name='edit_admin'),
    path('admins/<int:pk>/delete/', views.delete_admin, name='delete_admin'),
    
    # ====== سجل التدقيق ======
    path('audit-log/', views.audit_log, name='audit_log'),
    
    # ====== إدارة التخصصات والمهارات ======
    path('majors/', views.manage_majors, name='manage_majors'),
    path('skills/', views.manage_skills, name='manage_skills'),
    
    # ====== الإشعارات ======
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark-read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),
    path('update-notification-preferences/', views.update_notification_preferences, name='update_notification_preferences'),
    
    # ====== قصص النجاح ======
    path('success-story/create/', views.create_success_story, name='create_success_story'),
    path('success-stories/', views.success_stories_list, name='success_stories_list'),
    path('success-story/approve/<int:pk>/', views.approve_success_story, name='approve_success_story'),
    path('success-story/reject/<int:pk>/', views.reject_success_story, name='reject_success_story'),
    path('success-story/<int:pk>/delete/', views.delete_success_story, name='delete_success_story'),  # ✅ حذف قصة
    
    # ====== الموافقات المركزية (Pending Requests) ======
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    
    # ====== الموافقة على المجموعات ======
    path('group/<int:pk>/approve/', views.approve_group, name='approve_group'),
    path('group/<int:pk>/reject/', views.reject_group, name='reject_group'),
    path('group/<int:pk>/delete/', views.delete_group, name='delete_group'),  # ✅ حذف مجموعة
    
    # ====== الموافقة على الخريجين ======
    path('approve-graduate/<int:pk>/', views.approve_graduate, name='approve_graduate'),
    
    # ====== واجهات API ======
    path('stats/', views.get_dashboard_stats, name='stats'),
    
    # ====== التصدير ======
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]