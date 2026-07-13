from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import NormalUser, Profile, EmailVerification
from .utils import send_verification_email
import secrets


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(f"محاولة تسجيل دخول: {username}")  # للتصحيح
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # ✅ التحقق من أن المستخدم قد أكد بريده الإلكتروني
            try:
                profile = Profile.objects.get(user=user)
                if not profile.is_email_verified:
                    messages.warning(request, '⚠️ يرجى تأكيد بريدك الإلكتروني أولاً. تم إرسال رمز تأكيد جديد.')
                    # إرسال رمز جديد
                    verification, created = EmailVerification.objects.get_or_create(user=user)
                    code = verification.generate_code()
                    send_verification_email(user, code)
                    return redirect('accounts:verify_email', user_id=user.id)  # ✅ تم التعديل
            except Profile.DoesNotExist:
                # إنشاء بروفايل إذا لم يكن موجوداً
                profile = Profile.objects.create(user=user, is_email_verified=False)
            
            login(request, user)
            print(f"✅ نجح تسجيل الدخول: {username}")  # للتصحيح
            messages.success(request, f'مرحباً {username}، تم تسجيل الدخول بنجاح')
            return redirect('home')
        else:
            print(f"❌ فشل تسجيل الدخول: {username}")  # للتصحيح
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('home')

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
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '❌ البريد الإلكتروني مستخدم بالفعل')
            return render(request, 'accounts/register.html')
        
        # ✅ إنشاء المستخدم (غير مفعل حتى التحقق من البريد)
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            email=email,
            password=password
        )
        user.is_active = False  # 🔒 غير مفعل حتى التحقق
        user.save()
        
        # ✅ إنشاء بروفايل
        profile = Profile.objects.create(
            user=user,
            is_email_verified=False
        )
        
        # ✅ إنشاء NormalUser
        NormalUser.objects.create(
            user=user,
            phone='',  # يمكن للمستخدم إضافته لاحقاً
            is_graduate=False,
            is_employer=False
        )
        
        # ✅ توليد وإرسال رمز التأكيد
        verification = EmailVerification.objects.create(user=user)
        code = verification.generate_code()
        send_verification_email(user, code)
        
        messages.success(request, f'✅ تم إرسال رمز التأكيد إلى بريدك الإلكتروني ({email})')
        
        # ✅ استخدام الرابط المباشر بدلاً من redirect
        return redirect(f'/accounts/verify/{user.id}/')  # ← هذا هو الحل
    
    return render(request, 'accounts/register.html')
# ============================================================
# ✅ دوال التحقق عبر البريد الإلكتروني
# ============================================================

def verify_email_view(request, user_id):
    """صفحة إدخال رمز التأكيد"""
    try:
        user = User.objects.get(id=user_id)
        verification = EmailVerification.objects.get(user=user)
        profile = Profile.objects.get(user=user)
    except (User.DoesNotExist, EmailVerification.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, '❌ رابط غير صالح')
        return redirect('accounts:register')  # ✅ تم التعديل
    
    # ✅ إذا كان المستخدم قد تحقق بالفعل
    if profile.is_email_verified:
        messages.info(request, '✅ تم التحقق من بريدك الإلكتروني مسبقاً')
        return redirect('accounts:login')  # ✅ تم التعديل
    
    # ✅ إذا انتهت صلاحية الرمز
    if verification.is_expired():
        messages.warning(request, '⚠️ انتهت صلاحية الرمز، تم إرسال رمز جديد')
        verification.generate_code()
        send_verification_email(user, verification.code)
        return render(request, 'accounts/verify_email.html', {
            'user_id': user_id,
            'email': user.email
        })
    
    # ✅ إذا تم حظر المستخدم بسبب كثرة المحاولات
    if verification.is_blocked():
        messages.error(request, '❌ تم حظر حسابك مؤقتاً بسبب كثرة المحاولات الفاشلة. يرجى إعادة إرسال الرمز.')
        return render(request, 'accounts/verify_email.html', {
            'user_id': user_id,
            'email': user.email,
            'is_blocked': True
        })
    
    if request.method == 'POST':
        entered_code = request.POST.get('code')
        
        if entered_code == verification.code:
            # ✅ تأكيد التحقق
            verification.is_verified = True
            verification.save()
            
            # ✅ تفعيل المستخدم
            user.is_active = True
            user.save()
            
            # ✅ تحديث البروفايل
            profile.is_email_verified = True
            profile.save()
            
            messages.success(request, '🎉 تم تأكيد حسابك بنجاح! يمكنك تسجيل الدخول الآن.')
            return redirect('accounts:login')  # ✅ تم التعديل
        else:
            # ✅ زيادة عدد المحاولات الفاشلة
            verification.increment_attempts()
            
            if verification.is_blocked():
                messages.error(request, '❌ تم حظر حسابك مؤقتاً بسبب كثرة المحاولات الفاشلة. يرجى إعادة إرسال الرمز.')
            else:
                remaining = 5 - verification.attempts
                messages.error(request, f'❌ رمز غير صحيح. تبقى لك {remaining} محاولات.')
    
    return render(request, 'accounts/verify_email.html', {
        'user_id': user_id,
        'email': user.email,
        'is_blocked': verification.is_blocked()
    })


def resend_verification_code(request, user_id):
    """إعادة إرسال رمز التأكيد"""
    try:
        user = User.objects.get(id=user_id)
        verification = EmailVerification.objects.get(user=user)
        profile = Profile.objects.get(user=user)
    except (User.DoesNotExist, EmailVerification.DoesNotExist, Profile.DoesNotExist):
        messages.error(request, '❌ مستخدم غير موجود')
        return redirect('accounts:register')  # ✅ تم التعديل
    
    # ✅ إذا كان المستخدم قد تحقق بالفعل
    if profile.is_email_verified:
        messages.info(request, '✅ حسابك مفعل بالفعل')
        return redirect('accounts:login')  # ✅ تم التعديل
    
    # ✅ توليد رمز جديد وإرساله
    code = verification.generate_code()
    send_verification_email(user, code)
    
    messages.success(request, f'✅ تم إرسال رمز تأكيد جديد إلى بريدك الإلكتروني ({user.email})')
    return redirect('accounts:verify_email', user_id=user_id)  # ✅ تم التعديل


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
        
        # ✅ إنشاء NormalUser
        NormalUser.objects.create(
            user=user,
            phone=phone
        )
        
        # ✅ إنشاء بروفايل
        Profile.objects.create(
            user=user,
            is_email_verified=True  # ✅ مفترض أنه موثوق
        )
        
        login(request, user)
        messages.success(request, f'🎉 مرحباً {full_name}، تم تسجيل دخولك بنجاح!')
        return redirect('home')
    
    return redirect('landing')


@login_required
def account_view(request):
    return render(request, 'accounts/account.html', {'user': request.user})