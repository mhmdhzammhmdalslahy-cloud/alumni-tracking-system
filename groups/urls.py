from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    # المجموعات الأساسية
    path('', views.group_list, name='group_list'),
    path('create/', views.create_group, name='create_group'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:pk>/join/', views.join_group, name='join_group'),
    path('<int:pk>/leave/', views.leave_group, name='leave_group'),
    path('<int:pk>/approve/', views.approve_group, name='approve_group'),
    path('<int:pk>/reject/', views.reject_group, name='reject_group'),
    
    # المنتدى (المواضيع والتعليقات)
    path('<int:group_pk>/topics/', views.topic_list, name='topic_list'),
    path('<int:group_pk>/topics/create/', views.create_topic, name='create_topic'),
    path('<int:group_pk>/topics/<int:topic_pk>/', views.topic_detail, name='topic_detail'),
]