from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
import time

from .models import Group, Topic, Comment, CallRoom, RoomParticipant
from graduates.models import Graduate
from dashboard.models import Notification

# ============================================================
# ========== قائمة المجموعات ==========
# ============================================================

@login_required
def group_list(request):
    """عرض جميع المجموعات المتاحة للخريجين"""
    if request.user.is_staff:
        groups = Group.objects.filter(is_active=True).order_by('-created_at')
    else:
        groups = Group.objects.filter(is_active=True, status='approved').order_by('-created_at')
    
    try:
        graduate = request.user.graduate_profile
        for group in groups:
            group.is_member = graduate in group.members.all()
    except:
        pass
    
    return render(request, 'groups/group_list.html', {'groups': groups})
# ============================================================
# ========== إدارة المجموعات الأساسية ==========
# ============================================================

@login_required
def group_detail(request, pk):
    """عرض تفاصيل المجموعة"""
    group = get_object_or_404(Group, pk=pk, is_active=True)
    
    if not request.user.is_staff and group.status != 'approved':
        messages.error(request, 'هذه المجموعة غير متاحة حالياً (قيد المراجعة أو مرفوضة).')
        return redirect('groups:group_list')
    
    try:
        graduate = request.user.graduate_profile
        is_member = graduate in group.members.all()
    except:
        graduate = None
        is_member = False
    
    # التحقق من وجود مكالمة نشطة
    has_active_call = CallRoom.objects.filter(
        group=group,
        status='active'
    ).exists()
    
    # التحقق من البث المباشر النشط (مزامنة مع session)
    is_streaming = request.session.get(f'stream_active_{pk}', False)
    
    context = {
        'group': group,
        'is_member': is_member,
        'graduate': graduate,
        'has_active_call': has_active_call,
        'active_call': has_active_call,
        'is_streaming': is_streaming,
        'member_count': group.members.count(),
    }
    return render(request, 'groups/group_detail.html', context)


@login_required
def create_group(request):
    """إنشاء مجموعة جديدة"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'الرجاء إدخال اسم المجموعة')
            return render(request, 'groups/group_form.html')
        
        if Group.objects.filter(name=name).exists():
            messages.error(request, 'اسم المجموعة موجود مسبقاً. الرجاء اختيار اسم آخر.')
            return render(request, 'groups/group_form.html')
        
        group = Group.objects.create(
            name=name,
            description=description,
            category=category,
            image=image,
            created_by=request.user,
            status='pending',
            is_active=True
        )
        
        try:
            graduate = request.user.graduate_profile
            group.members.add(graduate)
        except:
            pass
        
        messages.success(request, f'تم إنشاء المجموعة "{name}" بنجاح. سيتم مراجعتها من قبل الإدارة قريباً.')
        return redirect('groups:group_detail', pk=group.pk)
    
    return render(request, 'groups/group_form.html')


@login_required
def join_group(request, pk):
    """الانضمام إلى مجموعة"""
    group = get_object_or_404(Group, pk=pk, is_active=True)
    
    if group.status != 'approved':
        messages.error(request, 'لا يمكن الانضمام إلى مجموعة غير موافق عليها بعد.')
        return redirect('groups:group_detail', pk=pk)
    
    try:
        graduate = request.user.graduate_profile
        if graduate not in group.members.all():
            group.members.add(graduate)
            messages.success(request, f'انضممت إلى مجموعة "{group.name}"')
        else:
            messages.info(request, 'أنت بالفعل عضو في هذه المجموعة')
    except:
        messages.error(request, 'يجب أن تكون خريجاً مسجلاً للانضمام للمجموعات')
    
    return redirect('groups:group_detail', pk=pk)


@login_required
def leave_group(request, pk):
    """مغادرة المجموعة"""
    group = get_object_or_404(Group, pk=pk, is_active=True)
    try:
        graduate = request.user.graduate_profile
        if graduate in group.members.all():
            group.members.remove(graduate)
            messages.success(request, f'غادرت مجموعة "{group.name}"')
    except:
        pass
    return redirect('groups:group_detail', pk=pk)


@staff_member_required
def approve_group(request, pk):
    """الموافقة على مجموعة (للمشرفين فقط)"""
    group = get_object_or_404(Group, pk=pk)
    group.status = 'approved'
    group.save()
    
    # إشعار لمنشئ المجموعة
    Notification.objects.create(
        recipient=group.created_by,
        title='✅ تم قبول مجموعتك',
        message=f'تمت الموافقة على مجموعتك "{group.name}" وأصبحت متاحة للأعضاء.',
        notification_type='success',
        link=f'/groups/{group.pk}/'
    )
    
    messages.success(request, f'✅ تم قبول مجموعة "{group.name}" بنجاح.')
    return redirect('groups:group_list')


@staff_member_required
def reject_group(request, pk):
    """رفض مجموعة (للمشرفين فقط)"""
    group = get_object_or_404(Group, pk=pk)
    group.status = 'rejected'
    group.save()
    
    # إشعار لمنشئ المجموعة
    Notification.objects.create(
        recipient=group.created_by,
        title='❌ تم رفض مجموعتك',
        message=f'تم رفض مجموعتك "{group.name}". يرجى التواصل مع الإدارة للمزيد من المعلومات.',
        notification_type='danger',
        link=f'/groups/{group.pk}/'
    )
    
    messages.warning(request, f'❌ تم رفض مجموعة "{group.name}".')
    return redirect('groups:group_list')


# ============================================================
# ========== المنتدى (المواضيع والتعليقات) ==========
# ============================================================

@login_required
def topic_list(request, group_pk):
    """قائمة المواضيع في المجموعة"""
    group = get_object_or_404(Group, pk=group_pk, is_active=True)
    
    if not request.user.is_staff and group.status != 'approved':
        messages.error(request, 'هذه المجموعة غير متاحة حالياً.')
        return redirect('groups:group_list')
    
    topics_list = group.topics.all().order_by('-updated_at', '-created_at')
    paginator = Paginator(topics_list, 5)
    page_number = request.GET.get('page')
    topics = paginator.get_page(page_number)
    
    return render(request, 'groups/topic_list.html', {'group': group, 'topics': topics})


@login_required
def create_topic(request, group_pk):
    """إنشاء موضوع جديد"""
    group = get_object_or_404(Group, pk=group_pk, is_active=True)
    
    if not request.user.is_staff and group.status != 'approved':
        messages.error(request, 'لا يمكن إنشاء مواضيع في مجموعة غير موافق عليها.')
        return redirect('groups:group_list')
    
    try:
        graduate = request.user.graduate_profile
        if graduate not in group.members.all():
            messages.error(request, 'يجب أن تكون عضواً في المجموعة لإنشاء موضوع.')
            return redirect('groups:group_detail', pk=group.pk)
    except:
        messages.error(request, 'يجب أن تكون خريجاً مسجلاً.')
        return redirect('groups:group_detail', pk=group.pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            topic = Topic.objects.create(
                group=group,
                title=title,
                content=content,
                created_by=request.user
            )
            messages.success(request, 'تم إنشاء الموضوع بنجاح.')
            return redirect('groups:topic_detail', group_pk=group.pk, topic_pk=topic.pk)
        else:
            messages.error(request, 'الرجاء ملء جميع الحقول.')
    
    return render(request, 'groups/create_topic.html', {'group': group})


@login_required
def topic_detail(request, group_pk, topic_pk):
    """عرض تفاصيل موضوع مع التعليقات"""
    group = get_object_or_404(Group, pk=group_pk, is_active=True)
    topic = get_object_or_404(Topic, pk=topic_pk, group=group)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        if content:
            comment = Comment.objects.create(
                topic=topic,
                content=content,
                created_by=request.user
            )
            if parent_id:
                try:
                    parent = Comment.objects.get(pk=parent_id)
                    comment.parent = parent
                    comment.save()
                except Comment.DoesNotExist:
                    pass
            messages.success(request, 'تم إضافة تعليقك.')
        else:
            messages.error(request, 'الرجاء كتابة تعليق.')
        return redirect('groups:topic_detail', group_pk=group.pk, topic_pk=topic.pk)
    
    # جلب التعليقات مع الردود
    comments = topic.comments.filter(parent=None).order_by('created_at')
    
    return render(request, 'groups/topic_detail.html', {
        'group': group,
        'topic': topic,
        'comments': comments
    })


@login_required
def topic_update(request, group_pk, topic_pk):
    """تعديل موضوع"""
    topic = get_object_or_404(Topic, pk=topic_pk, group_id=group_pk)
    
    if topic.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية تعديل هذا الموضوع.')
        return redirect('groups:topic_list', group_pk=group_pk)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            topic.title = title
            topic.content = content
            topic.save()
            messages.success(request, '✅ تم تحديث الموضوع.')
            return redirect('groups:topic_detail', group_pk=group_pk, topic_pk=topic_pk)
    
    return render(request, 'groups/topic_form.html', {'topic': topic, 'group': topic.group})


@login_required
def topic_delete(request, group_pk, topic_pk):
    """حذف موضوع"""
    topic = get_object_or_404(Topic, pk=topic_pk, group_id=group_pk)
    
    if topic.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية حذف هذا الموضوع.')
        return redirect('groups:topic_list', group_pk=group_pk)
    
    if request.method == 'POST':
        topic.delete()
        messages.success(request, '✅ تم حذف الموضوع.')
        return redirect('groups:topic_list', group_pk=group_pk)
    
    return render(request, 'groups/topic_confirm_delete.html', {'topic': topic})


# ============================================================
# ========== غرف البث والمكالمات ==========
# ============================================================

@login_required
def call_room(request, group_pk):
    """صفحة غرفة البث المباشر"""
    group = get_object_or_404(Group, pk=group_pk)
    
    # التحقق من وجود غرفة نشطة
    active_room = CallRoom.objects.filter(
        group=group,
        status='active'
    ).first()
    
    # إذا كانت هناك غرفة نشطة، استخدمها
    if active_room:
        room_name = f'room_{active_room.id}'
    else:
        room_name = f'group_{group_pk}'
    
    return render(request, 'groups/call_room.html', {
        'group': group,
        'room_name': room_name,
        'active_room': active_room
    })

@login_required
def live_stream(request, pk):
    """صفحة البث المباشر"""
    group = get_object_or_404(Group, pk=pk)
    
    # التحقق من العضوية
    try:
        graduate = request.user.graduate_profile
        is_member = graduate in group.members.all()
    except:
        is_member = False
    
    if not is_member and not request.user.is_staff:
        messages.error(request, 'يجب أن تكون عضواً في المجموعة للبث المباشر.')
        return redirect('groups:group_detail', pk=pk)
    
    # إنشاء معرف غرفة فريد
    room_name = f'group_{pk}_{int(time.time())}'
    
    # حفظ حالة البث في الجلسة
    request.session[f'stream_active_{pk}'] = True
    
    # إنشاء غرفة مكالمة إذا لم تكن موجودة
    active_room = CallRoom.objects.filter(
        group=group,
        status='active'
    ).first()
    
    if not active_room:
        try:
            active_room = CallRoom.objects.create(
                group=group,
                created_by=request.user,
                room_name=f'بث مباشر - {group.name}',
                status='active'
            )
            
            # إضافة المنشئ كمشارك
            RoomParticipant.objects.create(
                room=active_room,
                user=request.user,
                is_creator=True,
                is_online=True
            )
            
            # إشعار لأعضاء المجموعة
            for member in group.members.all():
                if member.user != request.user:
                    Notification.objects.create(
                        recipient=member.user,
                        title='📺 بث مباشر جديد',
                        message=f'{request.user.get_full_name()} بدأ بثاً مباشراً في "{group.name}"',
                        notification_type='info',
                        link=f'/groups/{pk}/live/'
                    )
        except Exception as e:
            print(f"Error creating room: {e}")
            # إذا فشل الإنشاء، استمر بدون غرفة
    
    context = {
        'group': group,
        'room_name': room_name,
        'active_room': active_room,
        'is_streaming': True,
        'user': request.user,
        'peer_id': request.session.get(f'peer_id_{pk}_{request.user.id}', None),
    }
    
    return render(request, 'groups/live_stream.html', context)

@login_required
def create_call_room(request, group_pk):
    """إنشاء غرفة مكالمة جديدة"""
    group = get_object_or_404(Group, pk=group_pk)
    
    # التحقق من وجود غرفة نشطة
    existing_room = CallRoom.objects.filter(
        group=group,
        status='active'
    ).exists()
    
    if existing_room:
        messages.warning(request, '⚠️ هناك مكالمة نشطة بالفعل في هذه المجموعة.')
        return redirect('groups:call_room', group_pk=group.pk)
    
    if request.method == 'POST':
        room_name = request.POST.get('room_name', f'غرفة {group.name}')
        room_type = request.POST.get('room_type', 'video')
        
        room = CallRoom.objects.create(
            group=group,
            created_by=request.user,
            room_name=room_name,
            room_type=room_type,
            status='active'
        )
        
        # إضافة المنشئ كمشارك
        RoomParticipant.objects.create(
            room=room,
            user=request.user,
            is_creator=True,
            is_online=True
        )
        
        # إشعار لأعضاء المجموعة
        for member in group.members.all():
            if member.user != request.user:
                Notification.objects.create(
                    recipient=member.user,
                    title=f'📹 غرفة فيديو جديدة',
                    message=f'{request.user.get_full_name()} فتح غرفة "{room_name}" في {group.name}',
                    notification_type='info',
                    link=f'/groups/room/{room.id}/'
                )
        
        messages.success(request, f'✅ تم إنشاء الغرفة "{room_name}" بنجاح!')
        return redirect('groups:call_room_detail', room_id=room.id)
    
    return render(request, 'groups/create_call_room.html', {'group': group})


@login_required
def call_room_detail(request, room_id):
    """عرض تفاصيل غرفة المكالمة"""
    room = get_object_or_404(CallRoom, pk=room_id)
    
    # التحقق من صلاحية الدخول
    if not room.group.members.filter(user=request.user).exists() and room.created_by != request.user:
        messages.error(request, 'ليس لديك صلاحية للدخول إلى هذه الغرفة.')
        return redirect('groups:group_detail', pk=room.group.pk)
    
    # إذا كانت الغرفة غير نشطة، إعادة التوجيه
    if room.status != 'active':
        messages.info(request, 'هذه الغرفة غير نشطة حالياً.')
        return redirect('groups:group_detail', pk=room.group.pk)
    
    # تحديث حالة المشارك
    participant, created = RoomParticipant.objects.get_or_create(
        room=room,
        user=request.user,
        defaults={'is_online': True}
    )
    if not created:
        participant.is_online = True
        participant.save()
    
    return render(request, 'groups/call_room.html', {
        'room': room,
        'group': room.group,
        'room_name': f'room_{room.id}',
        'is_creator': room.created_by == request.user,
    })


@login_required
def join_call_room(request, room_id):
    """الانضمام إلى غرفة مكالمة"""
    room = get_object_or_404(CallRoom, pk=room_id)
    
    if room.status != 'active':
        messages.error(request, 'هذه الغرفة غير نشطة.')
        return redirect('groups:group_detail', pk=room.group.pk)
    
    participant, created = RoomParticipant.objects.get_or_create(
        room=room,
        user=request.user,
        defaults={'is_online': True}
    )
    if not created:
        participant.is_online = True
        participant.save()
    
    messages.success(request, '✅ انضممت إلى الغرفة!')
    return redirect('groups:call_room_detail', room_id=room.id)


@login_required
def leave_call_room(request, room_id):
    """مغادرة غرفة المكالمة"""
    room = get_object_or_404(CallRoom, pk=room_id)
    
    try:
        participant = RoomParticipant.objects.get(room=room, user=request.user)
        participant.is_online = False
        participant.save()
    except RoomParticipant.DoesNotExist:
        pass
    
    messages.info(request, '👋 غادرت الغرفة.')
    return redirect('groups:group_detail', pk=room.group.pk)


@login_required
def end_call_room(request, room_id):
    """إنهاء غرفة المكالمة (للمنشئ فقط)"""
    room = get_object_or_404(CallRoom, pk=room_id)
    
    if room.created_by != request.user and not request.user.is_staff:
        messages.error(request, 'ليس لديك صلاحية إنهاء هذه الغرفة.')
        return redirect('groups:call_room_detail', room_id=room.id)
    
    room.status = 'ended'
    room.ended_at = timezone.now()
    room.save()
    
    # تحديث حالة جميع المشاركين
    RoomParticipant.objects.filter(room=room).update(is_online=False)
    
    # إشعار للمشاركين
    participants = RoomParticipant.objects.filter(room=room)
    for participant in participants:
        if participant.user != request.user:
            Notification.objects.create(
                recipient=participant.user,
                title='📹 انتهت المكالمة',
                message=f'انتهت مكالمة "{room.room_name}" في {room.group.name}',
                notification_type='info',
                link=f'/groups/{room.group.pk}/'
            )
    
    messages.success(request, '✅ تم إنهاء المكالمة بنجاح.')
    return redirect('groups:group_detail', pk=room.group.pk)


@login_required
def mute_participant(request, room_id, user_id):
    """كتم مشارك (للمنشئ فقط)"""
    if not request.user.is_staff:
        room = get_object_or_404(CallRoom, pk=room_id)
        if room.created_by != request.user:
            messages.error(request, 'غير مصرح لك بكتم المشاركين.')
            return redirect('groups:call_room_detail', room_id=room_id)
    
    participant = get_object_or_404(User, pk=user_id)
    room = get_object_or_404(CallRoom, pk=room_id)
    
    # تحديث حالة الكتم في قاعدة البيانات
    try:
        room_participant = RoomParticipant.objects.get(room=room, user=participant)
        room_participant.is_muted = not room_participant.is_muted
        room_participant.save()
        status = 'تم كتم' if room_participant.is_muted else 'تم إلغاء كتم'
        messages.success(request, f'🔇 {status} {participant.get_full_name()}.')
    except RoomParticipant.DoesNotExist:
        messages.error(request, 'المستخدم غير موجود في الغرفة.')
    
    return redirect('groups:call_room_detail', room_id=room.id)


# ============================================================
# ========== واجهات API للمكالمات ==========
# ============================================================

@login_required
def stream_status(request, group_pk):
    """API للتحقق من حالة البث"""
    group = get_object_or_404(Group, pk=group_pk)
    
    active_room = CallRoom.objects.filter(
        group=group,
        status='active'
    ).first()
    
    # التحقق من الجلسة أيضاً
    is_streaming = request.session.get(f'stream_active_{group_pk}', False)
    
    data = {
        'is_active': active_room is not None or is_streaming,
        'room_id': active_room.id if active_room else None,
        'room_name': active_room.room_name if active_room else None,
        'participants_count': RoomParticipant.objects.filter(
            room=active_room,
            is_online=True
        ).count() if active_room else 0,
        'created_by': active_room.created_by.get_full_name() if active_room else None,
        'streaming': is_streaming,
    }
    
    return JsonResponse(data)


@csrf_exempt
@login_required
def set_peer_id(request, group_pk):
    """API لحفظ Peer ID للمستخدم"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            peer_id = data.get('peer_id')
            
            if peer_id:
                # حفظ Peer ID في الجلسة
                request.session[f'peer_id_{group_pk}_{request.user.id}'] = peer_id
                
                # حفظ في قاعدة البيانات إذا كان هناك غرفة نشطة
                active_room = CallRoom.objects.filter(
                    group_id=group_pk,
                    status='active'
                ).first()
                
                if active_room:
                    participant, created = RoomParticipant.objects.get_or_create(
                        room=active_room,
                        user=request.user,
                        defaults={'is_online': True, 'peer_id': peer_id}
                    )
                    if not created:
                        participant.peer_id = peer_id
                        participant.is_online = True
                        participant.save()
                
                return JsonResponse({'success': True, 'peer_id': peer_id})
            else:
                return JsonResponse({'success': False, 'error': 'Peer ID مطلوب'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def add_like(request, group_pk):
    """API لإضافة إعجاب للبث"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            likes = data.get('likes', 0)
            
            # حفظ عدد الإعجابات في الجلسة
            request.session[f'stream_likes_{group_pk}'] = likes
            
            # تحديث في قاعدة البيانات إذا كانت هناك غرفة نشطة
            active_room = CallRoom.objects.filter(
                group_id=group_pk,
                status='active'
            ).first()
            
            if active_room:
                # يمكن إضافة حقل likes إلى نموذج CallRoom
                # active_room.likes = likes
                # active_room.save()
                pass
            
            return JsonResponse({
                'success': True,
                'likes': likes,
                'message': 'تم حفظ الإعجاب'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def add_comment(request, group_pk):
    """API لإضافة تعليق للبث"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            comment_text = data.get('comment', '')
            count = data.get('count', 0)
            
            # حفظ عدد التعليقات في الجلسة
            request.session[f'stream_comments_{group_pk}'] = count
            
            # حفظ التعليق في قاعدة البيانات
            if comment_text:
                group = get_object_or_404(Group, pk=group_pk)
                # يمكن إنشاء نموذج منفصل للتعليقات العامة
                # StreamComment.objects.create(group=group, user=request.user, comment=comment_text)
                
                # إشعار لمنشئ البث
                active_room = CallRoom.objects.filter(
                    group=group,
                    status='active'
                ).first()
                
                if active_room and active_room.created_by != request.user:
                    Notification.objects.create(
                        recipient=active_room.created_by,
                        title='💬 تعليق جديد',
                        message=f'{request.user.get_full_name()} علق: "{comment_text[:50]}..."',
                        notification_type='info',
                        link=f'/groups/{group_pk}/live/'
                    )
            
            return JsonResponse({
                'success': True,
                'comment': comment_text,
                'count': count,
                'message': 'تم حفظ التعليق'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
@login_required
def save_stream_status(request, group_pk):
    """API لحفظ حالة البث"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            is_active = data.get('is_active', False)
            
            group = get_object_or_404(Group, pk=group_pk)
            
            # حفظ في الجلسة
            request.session[f'stream_active_{group_pk}'] = is_active
            
            if is_active:
                # إنشاء غرفة نشطة إذا لم تكن موجودة
                active_room = CallRoom.objects.filter(
                    group=group,
                    status='active'
                ).first()
                
                if not active_room:
                    room = CallRoom.objects.create(
                        group=group,
                        created_by=request.user,
                        room_name=f'بث مباشر - {group.name}',
                        room_type='video',
                        status='active'
                    )
                    RoomParticipant.objects.create(
                        room=room,
                        user=request.user,
                        is_creator=True,
                        is_online=True
                    )
                    
                    # إشعار لأعضاء المجموعة
                    for member in group.members.all():
                        if member.user != request.user:
                            Notification.objects.create(
                                recipient=member.user,
                                title='📺 بث مباشر جديد',
                                message=f'{request.user.get_full_name()} بدأ بثاً مباشراً في "{group.name}"',
                                notification_type='info',
                                link=f'/groups/{group_pk}/live/'
                            )
            else:
                # إنهاء جميع الغرف النشطة
                CallRoom.objects.filter(
                    group=group,
                    status='active'
                ).update(status='ended', ended_at=timezone.now())
                
                RoomParticipant.objects.filter(
                    room__group=group,
                    room__status='ended'
                ).update(is_online=False)
            
            return JsonResponse({
                'success': True,
                'is_active': is_active,
                'message': 'تم تحديث حالة البث'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@login_required
def get_stream_participants(request, room_id):
    """API للحصول على قائمة المشاركين في البث"""
    room = get_object_or_404(CallRoom, pk=room_id)
    
    participants = RoomParticipant.objects.filter(
        room=room,
        is_online=True
    ).select_related('user')
    
    data = {
        'participants': [
            {
                'id': p.user.id,
                'name': p.user.get_full_name() or p.user.username,
                'is_creator': p.is_creator,
                'is_muted': p.is_muted,
            }
            for p in participants
        ],
        'count': participants.count(),
        'room_name': room.room_name,
        'is_active': room.status == 'active',
    }
    
    return JsonResponse(data)


# ============================================================
# ========== دوال مساعدة ==========
# ============================================================

def get_active_call(group):
    """الحصول على المكالمة النشطة لمجموعة"""
    return CallRoom.objects.filter(
        group=group,
        status='active'
    ).first()


def create_stream_notification(group, user, action='start'):
    """إنشاء إشعار للبث المباشر"""
    if action == 'start':
        title = '📺 بث مباشر جديد'
        message = f'{user.get_full_name()} بدأ بثاً مباشراً في "{group.name}"'
    else:
        title = '📺 انتهى البث المباشر'
        message = f'انتهى البث المباشر في "{group.name}"'
    
    for member in group.members.all():
        if member.user != user:
            Notification.objects.create(
                recipient=member.user,
                title=title,
                message=message,
                notification_type='info',
                link=f'/groups/{group.pk}/'
            )