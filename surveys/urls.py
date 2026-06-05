from django.urls import path
from . import views

urlpatterns = [
    path('', views.survey_list, name='survey_list'),
    path('<int:pk>/', views.take_survey, name='take_survey'),
    path('<int:pk>/results/', views.survey_results, name='survey_results'),
]