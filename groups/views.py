from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Group, Topic, Comment
from graduates.models import Graduate

# ========== إدارة المجموعات الأساسية ==========

@login_required
def group_list(request):
    # عرض المجموعات حسب صلاحية المستخدم
    if request.user.is_staff:
        groups = Group.objects.filter(is_active=True).order_by('-created_at')
    else:
        groups = Group.objects.filter(is_active=True, status='approved').order_by('-created_at')
    
    try:
        graduate = request.user.graduate_profile
        my_groups = graduate.joined_groups.all()
    except:
        graduate = None
        my_groups = []
    
    context = {
        'groups': groups,
        'my_groups': my_groups,
        'graduate': graduate,
    }
    return render(request, 'groups/group_list.html', context)

@login_required
def group_detail(request, pk):
    group = get_object_or_404(Group, pk=pk, is_active=True)
    # فقط المشرف أو إذا كانت المجموعة موافق عليها يمكن للمستخدم العادي رؤيتها
    if not request.user.is_staff and group.status != 'approved':
        messages.error(request, 'هذه المجموعة غير متاحة حالياً (قيد المراجعة أو مرفوضة).')
        return redirect('groups:group_list')
    
    try:
        graduate = request.user.graduate_profile
        is_member = graduate in group.members.all()
    except:
        graduate = None
        is_member = False
    
    context = {
        'group': group,
        'is_member': is_member,
        'graduate': graduate,
    }
    return render(request, 'groups/group_detail.html', context)

@login_required
def create_group(request):
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
    group = get_object_or_404(Group, pk=pk)
    group.status = 'approved'
    group.save()
    messages.success(request, f'✅ تم قبول مجموعة "{group.name}" بنجاح.')
    return redirect('groups:group_list')

@staff_member_required
def reject_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.status = 'rejected'
    group.save()
    messages.warning(request, f'❌ تم رفض مجموعة "{group.name}".')
    return redirect('groups:group_list')

# ========== المنتدى (المواضيع والتعليقات) ==========

@login_required
def topic_list(request, group_pk):
    group = get_object_or_404(Group, pk=group_pk, is_active=True)
    if not request.user.is_staff and group.status != 'approved':
        messages.error(request, 'هذه المجموعة غير متاحة حالياً.')
        return redirect('groups:group_list')
    topics = group.topics.all()
    return render(request, 'groups/topic_list.html', {'group': group, 'topics': topics})

@login_required
def create_topic(request, group_pk):
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
            Topic.objects.create(
                group=group,
                title=title,
                content=content,
                created_by=request.user
            )
            messages.success(request, 'تم إنشاء الموضوع بنجاح.')
            return redirect('groups:topic_list', group_pk=group.pk)
        else:
            messages.error(request, 'الرجاء ملء جميع الحقول.')
    
    return render(request, 'groups/create_topic.html', {'group': group})

@login_required
def topic_detail(request, group_pk, topic_pk):
    group = get_object_or_404(Group, pk=group_pk, is_active=True)
    topic = get_object_or_404(Topic, pk=topic_pk, group=group)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                topic=topic,
                content=content,
                created_by=request.user
            )
            messages.success(request, 'تم إضافة تعليقك.')
        else:
            messages.error(request, 'الرجاء كتابة تعليق.')
        return redirect('groups:topic_detail', group_pk=group.pk, topic_pk=topic.pk)
    
    return render(request, 'groups/topic_detail.html', {'group': group, 'topic': topic})