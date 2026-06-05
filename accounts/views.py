from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random
from .models import NormalUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'مرحباً {username}، تم تسجيل الدخول بنجاح')
            return redirect('home')
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('landing')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, '❌ كلمة المرور غير متطابقة')
            return render(request, 'accounts/register.html')
        
        if len(password) < 4:
            messages.error(request, '❌ كلمة المرور قصيرة جداً (4 أحرف على الأقل)')
            return render(request, 'accounts/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '❌ اسم المستخدم موجود بالفعل')
            return render(request, 'accounts/register.html')
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            email=email,
            password=password
        )
        
        messages.success(request, '🎉 تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن')
        return redirect('login')
    
    return render(request, 'accounts/register.html')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

def simple_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'البريد الإلكتروني مستخدم بالفعل')
            return redirect('landing')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'هذا البريد مستخدم بالفعل')
            return redirect('landing')
        
        # إنشاء مستخدم (اسم المستخدم = البريد الإلكتروني)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.first_name = full_name
        user.save()
        
        from .models import NormalUser
        NormalUser.objects.create(
            user=user,
            phone=phone
        )
        
        login(request, user)
        messages.success(request, f'🎉 مرحباً {full_name}، تم تسجيل دخولك بنجاح!')
        return redirect('home')
    
    return redirect('landing')