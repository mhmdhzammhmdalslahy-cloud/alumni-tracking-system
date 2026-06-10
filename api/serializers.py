from rest_framework import serializers
from graduates.models import Graduate, WorkExperience, Skill, Certification
from employers.models import Employer
from jobs.models import Job, JobApplication
from dashboard.models import Notification, SuccessStory
from groups.models import Group, Topic, Comment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class GraduateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Graduate
        fields = '__all__'
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Employer
        fields = '__all__'


class JobSerializer(serializers.ModelSerializer):
    employer_name = serializers.CharField(source='employer.company_name', read_only=True)
    
    class Meta:
        model = Job
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = '__all__'
    
    def get_comment_count(self, obj):
        return obj.comments.count()


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class SuccessStorySerializer(serializers.ModelSerializer):
    graduate_name = serializers.SerializerMethodField()
    author_type_display = serializers.CharField(source='get_author_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SuccessStory
        fields = '__all__'
    
    def get_graduate_name(self, obj):
        return obj.graduate.user.get_full_name() or obj.graduate.user.username


class GroupSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = '__all__'
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                graduate = request.user.graduate_profile
                return graduate in obj.members.all()
            except:
                pass
        return False


# Optional: إذا أردت إضافة serializers للـ WorkExperience, Skill, Certification, JobApplication
class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'


class JobApplicationSerializer(serializers.ModelSerializer):
    graduate_name = serializers.CharField(source='graduate.user.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = '__all__'