from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView  # ✅ أضف هذا
from graduates.views import home
from . import views
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    # ✅ الصفحة الرئيسية = صفحة تسجيل الدخول
    path('', LoginView.as_view(template_name='accounts/login.html'), name='login'),
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