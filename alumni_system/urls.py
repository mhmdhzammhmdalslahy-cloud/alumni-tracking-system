from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from graduates.views import home
from . import views
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ============================================================
    # ✅ الصفحة الرئيسية = صفحة تسجيل الدخول
    # ============================================================
    path('', LoginView.as_view(template_name='registration/login.html'), name='login'),  # ✅ تم التعديل
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # ============================================================
    # ✅ إعادة تعيين كلمة المرور (Password Reset)
    # ============================================================
    path('accounts/password/reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ),
         name='password_reset'),
    
    path('accounts/password/reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('accounts/password/reset/confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    
    path('accounts/password/reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # ============================================================
    # ✅ Allauth (تسجيل جوجل، نسيت كلمة المرور)
    # ============================================================
    path('auth/', include('allauth.urls')),
    
    # ============================================================
    # ✅ 2FA (معلق)
    # ============================================================
    # path('2fa/', include('two_factor.urls')),
    
    # ============================================================
    # ✅ تطبيقات المشروع
    # ============================================================
    path('home/', home, name='home'),
    path('graduates/', include('graduates.urls')),
    path('accounts/', include('accounts.urls')),
    path('employers/', include('employers.urls')),
    path('jobs/', include('jobs.urls')),
    path('surveys/', include('surveys.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),
    path('search/', views.search_all, name='search_all'),
    path('groups/', include('groups.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('api/', include('api.urls')),
    path('setlang/<str:language_code>/', views.set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)