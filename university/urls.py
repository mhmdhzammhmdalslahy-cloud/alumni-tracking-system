from django.urls import path
from . import views

app_name = 'university'

urlpatterns = [
    # ====== الصفحة الرئيسية ======
    path('', views.university_hub, name='hub'),
    
    # ====== الأخبار والإعلانات ======
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    
    # ====== التقويم الأكاديمي ======
    path('calendar/', views.calendar_list, name='calendar_list'),
    path('calendar/', views.calendar_list, name='calendar'),  # ✅ اسم مستعار للتوافق مع القالب
    
    # ====== الخدمات الرئيسية ======
    path('career-center/', views.career_center, name='career_center'),
    path('digital-library/', views.digital_library, name='digital_library'),
    path('continuing-education/', views.continuing_education, name='continuing_education'),
    path('market-analysis/', views.market_analysis, name='market_analysis'),
    
    # ====== تفاصيل المواد الدراسية ======
    path('material/<int:pk>/', views.study_material_detail, name='study_material_detail'),
    
    # ====== الشركاء ======
    path('partners/', views.partner_list, name='partner_list'),
    
    # ====== الوظائف ======
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    
    # ====== الدورات ======
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
]