from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from graduates.views import home
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # ← هذا السطر المعدل
    path('home/', home, name='home_url'),
    path('graduates/', include('graduates.urls')),
    path('accounts/', include('accounts.urls')),
    path('employers/', include('employers.urls')),
    path('jobs/', include('jobs.urls')),
    path('surveys/', include('surveys.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', TemplateView.as_view(template_name='sitemap.xml', content_type='application/xml')),
    path('search/', views.search_all, name='search_all'),
    path('groups/', include('groups.urls')),   # <-- جديد
    path('chatbot/', include('chatbot.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)