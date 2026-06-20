from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    # ============================================================
    # ========== المجموعات الأساسية ==========
    # ============================================================
    path('', views.group_list, name='group_list'),
    path('create/', views.create_group, name='create_group'),
    path('<int:pk>/', views.group_detail, name='group_detail'),
    path('<int:pk>/join/', views.join_group, name='join_group'),
    path('<int:pk>/leave/', views.leave_group, name='leave_group'),
    path('<int:pk>/approve/', views.approve_group, name='approve_group'),
    path('<int:pk>/reject/', views.reject_group, name='reject_group'),
    
    # ============================================================
    # ========== المنتدى (المواضيع والتعليقات) ==========
    # ============================================================
    path('<int:group_pk>/topics/', views.topic_list, name='topic_list'),
    path('<int:group_pk>/topics/create/', views.create_topic, name='create_topic'),
    path('<int:group_pk>/topics/<int:topic_pk>/', views.topic_detail, name='topic_detail'),
    path('<int:group_pk>/topics/<int:topic_pk>/update/', views.topic_update, name='topic_update'),
    path('<int:group_pk>/topics/<int:topic_pk>/delete/', views.topic_delete, name='topic_delete'),
    
    # ============================================================
    # ========== غرف البث والمكالمات ==========
    # ============================================================
    # صفحة البث المباشر (المسار الرئيسي)
    path('<int:pk>/live/', views.live_stream, name='live_stream'),
    
    # صفحة غرفة المكالمة
    path('<int:group_pk>/call/', views.call_room, name='call_room'),
    
    # إنشاء غرفة جديدة
    path('create-room/<int:group_pk>/', views.create_call_room, name='create_call_room'),
    
    # تفاصيل الغرفة
    path('room/<int:room_id>/', views.call_room_detail, name='call_room_detail'),
    
    # الانضمام والمغادرة
    path('room/<int:room_id>/join/', views.join_call_room, name='join_call_room'),
    path('room/<int:room_id>/leave/', views.leave_call_room, name='leave_call_room'),
    
    # إنهاء الغرفة (للمنشئ فقط)
    path('room/<int:room_id>/end/', views.end_call_room, name='end_call_room'),
    
    # كتم مشارك (للمنشئ فقط)
    path('room/<int:room_id>/mute/<int:user_id>/', views.mute_participant, name='mute_participant'),
    
    # ============================================================
    # ========== واجهات API (AJAX) ==========
    # ============================================================
    # التحقق من حالة البث (نسخة للـ live)
    path('<int:group_pk>/stream-status/', views.stream_status, name='stream_status'),
    
    # حفظ Peer ID
    path('<int:group_pk>/set-peer-id/', views.set_peer_id, name='set_peer_id'),
    
    # حفظ حالة البث
    path('<int:group_pk>/save-stream-status/', views.save_stream_status, name='save_stream_status'),
    
    # حفظ الإعجابات
    path('<int:group_pk>/like/', views.add_like, name='add_like'),
    
    # حفظ التعليقات
    path('<int:group_pk>/comment/', views.add_comment, name='add_comment'),
    
    # الحصول على قائمة المشاركين في الغرفة
    path('room/<int:room_id>/participants/', views.get_stream_participants, name='get_stream_participants'),
]

# ============================================================
# ========== أسماء المسارات المستخدمة في القوالب ==========
# ============================================================
"""
أمثلة على استخدام المسارات في القوالب:

1. قائمة المجموعات:
   {% url 'groups:group_list' %}

2. تفاصيل مجموعة:
   {% url 'groups:group_detail' group.id %}

3. البث المباشر:
   {% url 'groups:live_stream' group.id %}

4. غرفة المكالمة:
   {% url 'groups:call_room' group.id %}

5. إنشاء غرفة:
   {% url 'groups:create_call_room' group.id %}

6. تفاصيل الغرفة:
   {% url 'groups:call_room_detail' room.id %}

7. الانضمام للغرفة:
   {% url 'groups:join_call_room' room.id %}

8. المغادرة من الغرفة:
   {% url 'groups:leave_call_room' room.id %}

9. إنهاء الغرفة:
   {% url 'groups:end_call_room' room.id %}

10. كتم مشارك:
    {% url 'groups:mute_participant' room.id user.id %}

11. API حالة البث:
    {% url 'groups:stream_status' group.id %}

12. API حفظ Peer ID:
    {% url 'groups:set_peer_id' group.id %}

13. API الإعجاب:
    {% url 'groups:add_like' group.id %}

14. API التعليق:
    {% url 'groups:add_comment' group.id %}

15. API المشاركين:
    {% url 'groups:get_stream_participants' room.id %}
"""