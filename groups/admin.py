from django.contrib import admin
from .models import Group, Topic, Comment

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'member_count', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('name', 'description')
    filter_horizontal = ('members',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'created_by', 'created_at')
    list_filter = ('group',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('topic', 'created_by', 'created_at')