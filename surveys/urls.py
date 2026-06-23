from django.urls import path
from . import views

app_name = 'surveys'  # ✅ أضف هذا السطر (الأهم)

urlpatterns = [
    path('', views.survey_list, name='survey_list'),
    path('<int:pk>/', views.take_survey, name='respond'),  # ✅ غيّر name إلى 'respond'
    path('<int:pk>/results/', views.survey_results, name='survey_results'),
]