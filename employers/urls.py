from django.urls import path
from . import views

urlpatterns = [
    # ============================================================
    # ========== إدارة الشركات ==========
    # ============================================================
    path('', views.EmployerListView.as_view(), name='employer_list'),
    path('<int:pk>/', views.EmployerDetailView.as_view(), name='employer_profile'),
    path('create/', views.EmployerCreateView.as_view(), name='employer_create'),
    path('<int:pk>/update/', views.EmployerUpdateView.as_view(), name='employer_update'),
    path('<int:pk>/delete/', views.EmployerDeleteView.as_view(), name='employer_delete'),
    path('<int:pk>/verify/', views.verify_employer, name='employer_verify'),
    path('<int:pk>/add-review/', views.add_review, name='add_review'),
    
    # ============================================================
    # ========== طلبات التوظيف ==========
    # ============================================================
    # ✅ قبول الطلب (مع عرض نموذج العرض الوظيفي)
    path('application/<int:app_id>/accept-page/', views.accept_application_page, name='accept_application_page'),
    
    # ✅ رفض الطلب (زر مباشر)
    path('application/<int:app_id>/reject/', views.reject_application, name='reject_application'),
    
    # ✅ تحديد مقابلة (دالة موحدة - بعد توحيد call_for_interview و interview_application_page)
    path('application/<int:app_id>/interview-page/', views.interview_application_page, name='interview_application_page'),
    
    # ❌ تم حذف المسار القديم لتجنب التكرار:
    # path('application/<int:app_id>/interview/', views.call_for_interview, name='call_for_interview'),
    
    # ============================================================
    # ========== البحث عن الخريجين ==========
    # ============================================================
    path('search-graduates/', views.search_graduates, name='search_graduates'),
]