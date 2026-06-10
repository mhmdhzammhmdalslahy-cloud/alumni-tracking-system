from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'graduates', views.GraduateViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'employers', views.EmployerViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'success-stories', views.SuccessStoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]