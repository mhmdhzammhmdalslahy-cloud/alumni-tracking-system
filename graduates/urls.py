from django.urls import path
from . import views

urlpatterns = [
    path('', views.GraduateListView.as_view(), name='graduate_list'),
    path('<int:pk>/', views.GraduateProfileView.as_view(), name='graduate_profile'),
    path('create/', views.GraduateCreateView.as_view(), name='graduate_create'),
    path('<int:pk>/update/', views.GraduateUpdateView.as_view(), name='graduate_update'),
    path('<int:pk>/delete/', views.GraduateDeleteView.as_view(), name='graduate_delete'),
    path('verify/', views.verify_graduate, name='verify_graduate'),
    path('search/', views.search_graduates, name='search_graduates'),
     path('update-notification-preferences/', views.update_notification_preferences, name='update_notification_preferences'),
]