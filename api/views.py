from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import (
    GraduateSerializer, JobSerializer, NotificationSerializer,
    EmployerSerializer, GroupSerializer, TopicSerializer,
    CommentSerializer, SuccessStorySerializer
)
from graduates.models import Graduate
from employers.models import Employer
from jobs.models import Job
from dashboard.models import Notification, SuccessStory
from groups.models import Group, Topic, Comment


class GraduateViewSet(viewsets.ModelViewSet):
    queryset = Graduate.objects.all().order_by('-created_at')
    serializer_class = GraduateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['major', 'graduation_year', 'current_job_status']
    search_fields = ['user__first_name', 'user__last_name', 'major']
    ordering_fields = ['created_at', 'graduation_year']


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['job_type', 'location']
    search_fields = ['title', 'employer__company_name']


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.none()

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'marked as read'})


class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all().order_by('-created_at')
    serializer_class = EmployerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['company_name', 'industry']


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.filter(is_active=True, status='approved').order_by('-created_at')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category']

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group = self.get_object()
        if request.user.is_authenticated:
            try:
                graduate = request.user.graduate_profile
                if graduate not in group.members.all():
                    group.members.add(graduate)
                    return Response({'status': 'joined'})
                else:
                    return Response({'status': 'already_member'}, status=400)
            except:
                return Response({'error': 'Not a graduate'}, status=400)
        return Response({'error': 'Not authenticated'}, status=401)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        group = self.get_object()
        if request.user.is_authenticated:
            try:
                graduate = request.user.graduate_profile
                if graduate in group.members.all():
                    group.members.remove(graduate)
                    return Response({'status': 'left'})
                else:
                    return Response({'status': 'not_member'}, status=400)
            except:
                return Response({'error': 'Not a graduate'}, status=400)
        return Response({'error': 'Not authenticated'}, status=401)


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all().order_by('-created_at')
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SuccessStoryViewSet(viewsets.ModelViewSet):
    queryset = SuccessStory.objects.filter(status='approved', is_active=True).order_by('-created_at')
    serializer_class = SuccessStorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'graduate__user__first_name', 'graduate__user__last_name']