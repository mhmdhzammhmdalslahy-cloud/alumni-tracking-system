from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import (
    AdminProfile, VerificationRequest, EmployerVerificationRequest,
    Survey, SurveyResponse, Event, EventAttendance, Report,
    SystemSetting, AuditLog, Major, Skill, BannedWord, SuccessStory,
    Notification
)
from .forms import (
    SurveyForm, EventForm, SystemSettingForm, AdminProfileForm,
    MajorForm, SkillForm, BannedWordForm, VerificationReviewForm,
    SuccessStoryForm
)
from graduates.models import Graduate
from graduates.forms import GraduateForm
from employers.models import Employer
from jobs.models import Job, JobApplication
from django.contrib.auth.models import User
from groups.models import Group
# ========== الصفحة الرئيسية للوحة التحكم ==========

@staff_member_required
def admin_dashboard(request):
    # حساب الأعداد الأساسية
    total_graduates = Graduate.objects.count()
    total_employers = Employer.objects.count()
    total_jobs = Job.objects.filter(is_active=True).count()
    total_applications = JobApplication.objects.count()
    
    # حساب الطلبات المعلقة
    pending_graduates_count = VerificationRequest.objects.filter(status='pending').count()
    pending_employers_count = EmployerVerificationRequest.objects.filter(status='pending').count()
    pending_stories_count = SuccessStory.objects.filter(status='pending').count()
    pending_groups_count = Group.objects.filter(status='pending', is_active=True).count()
    
    # جلب قصص النجاح المعلقة
    pending_success_stories = SuccessStory.objects.filter(status='pending')
    
    context = {
        'total_graduates': total_graduates,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'pending_graduates': pending_graduates_count,
        'pending_employers': pending_employers_count,
        'employment_rate': calculate_employment_rate(),
        'recent_graduates': Graduate.objects.all().order_by('-created_at')[:5],
        'recent_employers': Employer.objects.all().order_by('-created_at')[:5],
        'recent_applications': JobApplication.objects.all().order_by('-applied_at')[:5],
        'popular_majors': get_popular_majors(),
        'top_employers': get_top_employers(),
        'monthly_jobs': get_monthly_jobs(),
        'pending_success_stories': pending_success_stories,
        # متغيرات لعرض الأرقام في لوحة التحكم
        'pending_graduates_count': pending_graduates_count,
        'pending_employers_count': pending_employers_count,
        'pending_stories_count': pending_stories_count,
        'pending_groups_count': pending_groups_count,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


def calculate_employment_rate():
    total = Graduate.objects.count()
    if total == 0:
        return 0
    working = Graduate.objects.filter(current_job_status='working').count()
    return round((working / total) * 100, 1)


def get_popular_majors():
    return Graduate.objects.values('major').annotate(count=Count('id')).order_by('-count')[:5]


def get_top_employers():
    return Employer.objects.annotate(job_count=Count('jobs')).order_by('-job_count')[:5]


def get_monthly_jobs():
    from datetime import datetime, timedelta
    months = []
    counts = []
    for i in range(6):
        month = timezone.now() - timedelta(days=30*i)
        count = Job.objects.filter(created_at__month=month.month, created_at__year=month.year).count()
        months.append(month.strftime('%B'))
        counts.append(count)
    return {'months': months[::-1], 'counts': counts[::-1]}


# ========== إدارة الخريجين ==========

@staff_member_required
def manage_graduates(request):
    graduates = Graduate.objects.all().order_by('-created_at')
    
    search = request.GET.get('search', '')
    if search:
        graduates = graduates.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(university_id__icontains=search) |
            Q(major__icontains=search)
        )
    
    status = request.GET.get('status', '')
    if status:
        graduates = graduates.filter(is_verified=(status == 'verified'))
    
    major = request.GET.get('major', '')
    if major:
        graduates = graduates.filter(major__icontains=major)
    
    year = request.GET.get('year', '')
    if year:
        graduates = graduates.filter(graduation_year=year)
    
    paginator = Paginator(graduates, 20)
    page_number = request.GET.get('page', 1)
    graduates_page = paginator.get_page(page_number)
    
    context = {
        'graduates': graduates_page,
        'majors': Graduate.objects.values_list('major', flat=True).distinct(),
        'years': Graduate.objects.values_list('graduation_year', flat=True).distinct().order_by('-graduation_year'),
    }
    return render(request, 'dashboard/manage_graduates.html', context)


@staff_member_required
def verify_graduate(request, pk):
    graduate = get_object_or_404(Graduate, pk=pk)
    
    # محاولة جلب طلب توثيق معلق
    verification = VerificationRequest.objects.filter(graduate=graduate, status='pending').first()
    
    # إذا لم يكن هناك طلب معلق، قم بإنشائه تلقائياً
    if not verification:
        # إنشاء طلب توثيق جديد للخريج
        verification = VerificationRequest.objects.create(
            graduate=graduate,
            student_university_number=graduate.university_id,
            uploaded_document='',  # يمكن تركه فارغاً أو تعيين قيمة افتراضية
            status='pending'
        )
        messages.info(request, f'📝 تم إنشاء طلب توثيق تلقائي للخريج {graduate.user.get_full_name()}')
        # إعادة التوجيه إلى نفس الصفحة لتحديث النموذج
        return redirect('dashboard:verify_graduate', pk=graduate.pk)
    
    # إذا كان الطلب موجوداً، تابع العملية كالمعتاد
    if request.method == 'POST':
        form = VerificationReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'approve':
                verification.status = 'approved'
                graduate.is_verified = True
                graduate.user.is_active = True
                graduate.user.save()
                graduate.save()
                messages.success(request, f'✅ تم توثيق حساب {graduate.user.get_full_name()} بنجاح')
                
                # ========== إرسال رسالة ترحيب ==========
                # 1. إشعار داخلي (في قاعدة البيانات)
                Notification.objects.create(
                    recipient=graduate.user,
                    title='🎉 مرحباً بك في نظام متابعة الخريجين',
                    message=f'أهلاً {graduate.user.get_full_name()}، تم توثيق حسابك بنجاح. يمكنك الآن الاستفادة من جميع خدمات المنصة.',
                    notification_type='welcome',
                    link=f'/graduates/{graduate.id}/'
                )
                
                # 2. بريد إلكتروني ترحيبي
                try:
                    send_mail(
                        subject='🎉 مرحباً بك في نظام متابعة الخريجين',
                        message=f"""أهلاً {graduate.user.get_full_name()},

تم توثيق حسابك بنجاح في نظام متابعة الخريجين. يمكنك الآن:

- ✅ عرض وتحديث ملفك الشخصي
- ✅ التقدم للوظائف المتاحة
- ✅ المشاركة في المجموعات والمنتديات
- ✅ إضافة قصص نجاح
- ✅ استقبال إشعارات الوظائف الجديدة

نتمنى لك تجربة ممتعة!

فريق نظام متابعة الخريجين
""",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[graduate.user.email],
                        fail_silently=True,  # لا يظهر خطأ إذا فشل الإرسال
                    )
                except Exception as e:
                    # تسجيل الخطأ في السجلات (اختياري)
                    print(f"⚠️ فشل إرسال البريد الترحيبي لـ {graduate.user.email}: {e}")
                # ========== نهاية رسالة الترحيب ==========
                
            else:
                verification.status = 'rejected'
                verification.rejection_reason = form.cleaned_data['rejection_reason']
                graduate.is_verified = False
                graduate.user.is_active = False
                graduate.user.save()
                graduate.save()
                messages.warning(request, f'📝 تم رفض طلب توثيق {graduate.user.get_full_name()}')
            
            verification.reviewed_by = request.user.admin_profile
            verification.reviewed_at = timezone.now()
            verification.save()
            
            AuditLog.objects.create(
                admin=request.user.admin_profile,
                action='approve' if action == 'approve' else 'reject',
                target_type='graduate',
                target_id=graduate.id,
                details={'name': graduate.user.get_full_name()}
            )
            
            if action == 'approve':
                Notification.objects.create(
                    recipient=graduate.user,
                    title='✅ تم توثيق حسابك',
                    message=f'تم قبول طلب توثيق حسابك كخريج.',
                    notification_type='success',
                    link=f'/graduates/{graduate.id}/'
                )
            else:
                Notification.objects.create(
                    recipient=graduate.user,
                    title='❌ تم رفض طلب التوثيق',
                    message=f'عذراً، تم رفض طلب توثيق حسابك. السبب: {verification.rejection_reason}',
                    notification_type='danger',
                    link='/profile/'
                )
            
            return redirect('dashboard:manage_graduates')
    else:
        form = VerificationReviewForm()
    
    return render(request, 'dashboard/verify_graduate.html', {'graduate': graduate, 'verification': verification, 'form': form})
# ========== إدارة الشركات ==========

@staff_member_required
def manage_employers(request):
    employers = Employer.objects.all().order_by('-created_at')
    
    search = request.GET.get('search', '')
    if search:
        employers = employers.filter(
            Q(company_name__icontains=search) |
            Q(industry__icontains=search)
        )
    
    status = request.GET.get('status', '')
    if status:
        employers = employers.filter(is_verified=(status == 'verified'))
    
    industry = request.GET.get('industry', '')
    if industry:
        employers = employers.filter(industry=industry)
    
    paginator = Paginator(employers, 20)
    page_number = request.GET.get('page', 1)
    employers_page = paginator.get_page(page_number)
    
    context = {
        'employers': employers_page,
        'industries': Employer.objects.values_list('industry', flat=True).distinct(),
    }
    return render(request, 'dashboard/manage_employers.html', context)


@staff_member_required
def verify_employer(request, pk):
    employer = get_object_or_404(Employer, pk=pk)
    verification = get_object_or_404(EmployerVerificationRequest, employer=employer, status='pending')
    
    if request.method == 'POST':
        form = VerificationReviewForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'approve':
                verification.status = 'approved'
                employer.is_verified = True
                employer.user.is_active = True
                employer.user.save()
                employer.save()
                messages.success(request, f'✅ تم توثيق حساب {employer.company_name} بنجاح')
            else:
                verification.status = 'rejected'
                verification.rejection_reason = form.cleaned_data['rejection_reason']
                employer.is_verified = False
                employer.user.is_active = False
                employer.user.save()
                employer.save()
                messages.warning(request, f'📝 تم رفض طلب توثيق {employer.company_name}')
            
            verification.reviewed_by = request.user.admin_profile
            verification.reviewed_at = timezone.now()
            verification.save()
            
            AuditLog.objects.create(
                admin=request.user.admin_profile,
                action='approve' if action == 'approve' else 'reject',
                target_type='employer',
                target_id=employer.id,
                details={'name': employer.company_name}
            )
            
            if action == 'approve':
                Notification.objects.create(
                    recipient=employer.user,
                    title='✅ تم توثيق حساب شركتك',
                    message=f'تم قبول طلب توثيق شركة {employer.company_name}.',
                    notification_type='success',
                    link=f'/employers/{employer.id}/'
                )
            else:
                Notification.objects.create(
                    recipient=employer.user,
                    title='❌ تم رفض طلب التوثيق',
                    message=f'عذراً، تم رفض طلب توثيق شركتك. السبب: {verification.rejection_reason}',
                    notification_type='danger',
                    link='/employer/profile/'
                )
            
            return redirect('dashboard:manage_employers')
    else:
        form = VerificationReviewForm()
    
    return render(request, 'dashboard/verify_employer.html', {'employer': employer, 'verification': verification, 'form': form})


# ========== إدارة الاستبيانات ==========

@staff_member_required
def manage_surveys(request):
    surveys = Survey.objects.all().order_by('-created_at')
    paginator = Paginator(surveys, 20)
    page_number = request.GET.get('page', 1)
    surveys_page = paginator.get_page(page_number)
    return render(request, 'dashboard/manage_surveys.html', {'surveys': surveys_page})


@staff_member_required
def create_survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user.admin_profile
            survey.save()
            messages.success(request, '✅ تم إنشاء الاستبيان بنجاح')
            return redirect('dashboard:manage_surveys')
    else:
        form = SurveyForm()
    return render(request, 'dashboard/survey_form.html', {'form': form, 'title': 'إنشاء استبيان جديد'})


@staff_member_required
def edit_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    if request.method == 'POST':
        form = SurveyForm(request.POST, instance=survey)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم تحديث الاستبيان بنجاح')
            return redirect('dashboard:manage_surveys')
    else:
        form = SurveyForm(instance=survey)
    return render(request, 'dashboard/survey_form.html', {'form': form, 'title': 'تعديل الاستبيان'})


@staff_member_required
def delete_survey(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    survey.delete()
    messages.success(request, '✅ تم حذف الاستبيان بنجاح')
    return redirect('dashboard:manage_surveys')


# ========== إدارة الفعاليات ==========

@staff_member_required
def manage_events(request):
    events = Event.objects.all().order_by('-date')
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page', 1)
    events_page = paginator.get_page(page_number)
    return render(request, 'dashboard/manage_events.html', {'events': events_page})


@staff_member_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user.admin_profile
            event.save()
            messages.success(request, '✅ تم إنشاء الفعالية بنجاح')
            return redirect('dashboard:manage_events')
    else:
        form = EventForm()
    return render(request, 'dashboard/event_form.html', {'form': form, 'title': 'إنشاء فعالية جديدة'})


@staff_member_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم تحديث الفعالية بنجاح')
            return redirect('dashboard:manage_events')
    else:
        form = EventForm(instance=event)
    return render(request, 'dashboard/event_form.html', {'form': form, 'title': 'تعديل الفعالية'})


@staff_member_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    event.delete()
    messages.success(request, '✅ تم حذف الفعالية بنجاح')
    return redirect('dashboard:manage_events')


# ========== التقارير ==========

@staff_member_required
def reports(request):
    reports = Report.objects.all().order_by('-generated_at')
    return render(request, 'dashboard/reports.html', {'reports': reports})


@staff_member_required
def generate_report(request):
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        if report_type == 'employment':
            return render(request, 'dashboard/reports/employment_report.html', {
                'data': get_employment_report_data(None, None),
            })
        else:
            return render(request, 'dashboard/reports/general_report.html', {
                'data': get_general_report_data(),
            })
    return render(request, 'dashboard/generate_report.html')


def get_employment_report_data(start_date, end_date):
    graduates = Graduate.objects.all()
    if start_date:
        graduates = graduates.filter(created_at__gte=start_date)
    if end_date:
        graduates = graduates.filter(created_at__lte=end_date)
    return {
        'total': graduates.count(),
        'working': graduates.filter(current_job_status='working').count(),
        'seeking': graduates.filter(current_job_status='seeking').count(),
        'by_major': graduates.values('major').annotate(count=Count('id')),
    }


def get_skill_gap_report_data():
    from jobs.models import Job
    all_skills = set()
    job_skills = set()
    for grad in Graduate.objects.all():
        for skill in grad.skills.all():
            all_skills.add(skill.name.lower())
    for job in Job.objects.all():
        skills = job.required_skills.lower().split(',')
        for skill in skills:
            job_skills.add(skill.strip())
    gap_skills = job_skills - all_skills
    return {
        'total_skills': len(all_skills),
        'required_skills': len(job_skills),
        'gap_skills': list(gap_skills)[:20],
    }


def get_general_report_data():
    return {
        'total_graduates': Graduate.objects.count(),
        'total_employers': Employer.objects.count(),
        'total_jobs': Job.objects.count(),
        'total_applications': JobApplication.objects.count(),
    }


# ========== إعدادات النظام ==========

@staff_member_required
def system_settings(request):
    if not request.user.admin_profile.admin_level == 'super_admin':
        messages.error(request, 'غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect('dashboard:admin_dashboard')
    settings = SystemSetting.objects.all()
    if request.method == 'POST':
        for setting in settings:
            new_value = request.POST.get(setting.key)
            if new_value:
                setting.value = new_value
                setting.updated_by = request.user.admin_profile
                setting.save()
        messages.success(request, '✅ تم حفظ الإعدادات بنجاح')
        return redirect('dashboard:system_settings')
    return render(request, 'dashboard/system_settings.html', {'settings': settings})


# ========== إدارة المشرفين ==========

@staff_member_required
def manage_admins(request):
    if not request.user.admin_profile.admin_level == 'super_admin':
        messages.error(request, 'غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect('dashboard:admin_dashboard')
    admins = AdminProfile.objects.all().order_by('-created_at')
    return render(request, 'dashboard/manage_admins.html', {'admins': admins})


@staff_member_required
def add_admin(request):
    if not request.user.admin_profile.admin_level == 'super_admin':
        messages.error(request, 'غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect('dashboard:admin_dashboard')
    if request.method == 'POST':
        form = AdminProfileForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            admin.created_by = request.user.admin_profile
            admin.save()
            messages.success(request, f'✅ تم إضافة المشرف {admin.user.get_full_name()} بنجاح')
            return redirect('dashboard:manage_admins')
    else:
        form = AdminProfileForm()
    return render(request, 'dashboard/admin_form.html', {'form': form, 'title': 'إضافة مشرف جديد'})


@staff_member_required
def edit_admin(request, pk):
    if not request.user.admin_profile.admin_level == 'super_admin':
        messages.error(request, 'غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect('dashboard:admin_dashboard')
    admin = get_object_or_404(AdminProfile, pk=pk)
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=admin)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ تم تحديث بيانات المشرف {admin.user.get_full_name()} بنجاح')
            return redirect('dashboard:manage_admins')
    else:
        form = AdminProfileForm(instance=admin)
    return render(request, 'dashboard/admin_form.html', {'form': form, 'title': 'تعديل بيانات المشرف'})


@staff_member_required
def delete_admin(request, pk):
    if not request.user.admin_profile.admin_level == 'super_admin':
        messages.error(request, 'غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect('dashboard:admin_dashboard')
    admin = get_object_or_404(AdminProfile, pk=pk)
    if admin == request.user.admin_profile:
        messages.error(request, 'لا يمكنك حذف حسابك الخاص')
        return redirect('dashboard:manage_admins')
    admin.delete()
    messages.success(request, '✅ تم حذف المشرف بنجاح')
    return redirect('dashboard:manage_admins')


# ========== سجل التدقيق ==========

@staff_member_required
def audit_log(request):
    if not request.user.admin_profile.admin_level == 'super_admin':
        messages.error(request, 'غير مصرح لك بالوصول إلى هذه الصفحة')
        return redirect('dashboard:admin_dashboard')
    logs = AuditLog.objects.all().order_by('-created_at')
    action = request.GET.get('action', '')
    if action:
        logs = logs.filter(action=action)
    target = request.GET.get('target', '')
    if target:
        logs = logs.filter(target_type__icontains=target)
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page', 1)
    logs_page = paginator.get_page(page_number)
    return render(request, 'dashboard/audit_log.html', {'logs': logs_page})


# ========== إدارة التخصصات والمهارات (نسخة واحدة فقط) ==========

@staff_member_required
def manage_majors(request):
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            major = get_object_or_404(Major, id=request.POST['delete_id'])
            major.delete()
            messages.success(request, '✅ تم حذف التخصص بنجاح')
            return redirect('dashboard:manage_majors')
        form = MajorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم إضافة التخصص بنجاح')
            return redirect('dashboard:manage_majors')
    else:
        form = MajorForm()
    majors = Major.objects.all().order_by('name')
    return render(request, 'dashboard/manage_majors.html', {'majors': majors, 'form': form})


@staff_member_required
def manage_skills(request):
    if request.method == 'POST':
        if 'delete_id' in request.POST:
            skill = get_object_or_404(Skill, id=request.POST['delete_id'])
            skill.delete()
            messages.success(request, '✅ تم حذف المهارة بنجاح')
            return redirect('dashboard:manage_skills')
        form = SkillForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم إضافة المهارة بنجاح')
            return redirect('dashboard:manage_skills')
    else:
        form = SkillForm()
    skills = Skill.objects.all().order_by('name')
    return render(request, 'dashboard/manage_skills.html', {'skills': skills, 'form': form})


# ========== صلاحيات الخريج (تعديل/حذف ملفه فقط) ==========

class GraduateUpdateView(LoginRequiredMixin, UpdateView):
    model = Graduate
    form_class = GraduateForm
    template_name = 'graduates/graduate_form.html'
    success_url = reverse_lazy('graduate_list')
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'graduate_profile'):
            messages.error(request, 'يجب أن تكون مسجلاً كخريج')
            return redirect('graduate_create')
        return super().dispatch(request, *args, **kwargs)


class GraduateDeleteView(LoginRequiredMixin, DeleteView):
    model = Graduate
    success_url = reverse_lazy('graduate_list')
    template_name = 'graduates/graduate_confirm_delete.html'
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


# ========== الإشعارات ==========

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    return render(request, 'notifications/list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


@login_required
def mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    if notification.link:
        return redirect(notification.link)
    return redirect('notification_list')


# ========== قصص النجاح ==========

@login_required
def create_success_story(request):
    if request.method == 'POST':
        form = SuccessStoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.created_by = request.user
            try:
                graduate = request.user.graduate_profile
                story.graduate = graduate
                story.author_type = 'graduate'
            except:
                try:
                    from employers.models import Employer
                    employer = Employer.objects.get(user=request.user)
                    story.company = employer
                    story.author_type = 'company'
                    story.graduate = Graduate.objects.first()
                except:
                    messages.error(request, 'يجب أن تكون خريجاً أو شركة لنشر قصة نجاح.')
                    return redirect('home')
            story.status = 'pending'
            story.save()
            messages.success(request, 'تم إرسال قصتك للمراجعة. ستظهر بعد الموافقة.')
            return redirect('home')
    else:
        form = SuccessStoryForm()
    return render(request, 'dashboard/success_story_form.html', {'form': form})


def success_stories_list(request):
    stories = SuccessStory.objects.filter(status='approved', is_active=True)
    return render(request, 'dashboard/success_stories_list.html', {'stories': stories})


@staff_member_required
def approve_success_story(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk)
    story.status = 'approved'
    story.save()
    messages.success(request, 'تم قبول القصة بنجاح.')
    return redirect('dashboard:admin_dashboard')


@staff_member_required
def reject_success_story(request, pk):
    story = get_object_or_404(SuccessStory, pk=pk)
    story.status = 'rejected'
    story.save()
    messages.warning(request, 'تم رفض القصة.')
    return redirect('dashboard:admin_dashboard')


# ========== الموافقة على المجموعات ==========

@staff_member_required
def approve_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.status = 'approved'
    group.is_active = True
    group.save()
    
    if group.created_by:
        Notification.objects.create(
            recipient=group.created_by,
            title='✅ تم قبول مجموعتك',
            message=f'تمت الموافقة على مجموعتك "{group.name}" وأصبحت متاحة للخريجين.',
            notification_type='success',
            link=f'/groups/{group.id}/'
        )
    
    messages.success(request, f'✅ تم قبول مجموعة "{group.name}" بنجاح.')
    return redirect('dashboard:pending_requests')


@staff_member_required
def reject_group(request, pk):
    group = get_object_or_404(Group, pk=pk)
    group.status = 'rejected'
    group.is_active = False
    group.save()
    
    if group.created_by:
        Notification.objects.create(
            recipient=group.created_by,
            title='❌ تم رفض مجموعتك',
            message=f'عذراً، تم رفض مجموعتك "{group.name}". يمكنك التواصل مع الإدارة لمعرفة السبب.',
            notification_type='danger',
            link='/groups/'
        )
    
    messages.warning(request, f'❌ تم رفض مجموعة "{group.name}".')
    return redirect('dashboard:pending_requests')


# ========== صفحة الموافقات المركزية ==========

@staff_member_required
def pending_requests(request):
    pending_graduates = VerificationRequest.objects.filter(status='pending').select_related('graduate__user')
    pending_employers = EmployerVerificationRequest.objects.filter(status='pending').select_related('employer__user')
    pending_stories = SuccessStory.objects.filter(status='pending').select_related('graduate__user')
    pending_groups = Group.objects.filter(status='pending', is_active=True)
    
    context = {
        'pending_graduates': pending_graduates,
        'pending_employers': pending_employers,
        'pending_stories': pending_stories,
        'pending_groups': pending_groups,
    }
    return render(request, 'dashboard/pending_requests.html', context)


# ========== تعطيل/تفعيل مستخدم ==========

@staff_member_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = not user.is_active
    user.save()
    
    status_text = "تفعيل" if user.is_active else "تعطيل"
    messages.success(request, f'✅ تم {status_text} حساب {user.get_full_name() or user.username} بنجاح.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_dashboard'))

# ========== دوال الموافقة على المجموعات ==========

@staff_member_required
def approve_group(request, pk):
    """✅ قبول مجموعة (تصبح ظاهرة للخريجين)"""
    group = get_object_or_404(Group, pk=pk)
    group.status = 'approved'
    group.is_active = True
    group.save()
    
    # إشعار لمنشئ المجموعة
    if group.created_by:
        Notification.objects.create(
            recipient=group.created_by,
            title='✅ تم قبول مجموعتك',
            message=f'تمت الموافقة على مجموعتك "{group.name}" وأصبحت متاحة للخريجين.',
            notification_type='success',
            link=f'/groups/{group.id}/'
        )
    
    messages.success(request, f'✅ تم قبول مجموعة "{group.name}" بنجاح.')
    return redirect('dashboard:pending_requests')


@staff_member_required
def reject_group(request, pk):
    """❌ رفض مجموعة مع إشعار للمنشئ"""
    group = get_object_or_404(Group, pk=pk)
    group.status = 'rejected'
    group.is_active = False
    group.save()
    
    # إشعار لمنشئ المجموعة
    if group.created_by:
        Notification.objects.create(
            recipient=group.created_by,
            title='❌ تم رفض مجموعتك',
            message=f'عذراً، تم رفض مجموعتك "{group.name}". يمكنك التواصل مع الإدارة لمعرفة السبب.',
            notification_type='danger',
            link='/groups/'
        )
    
    messages.warning(request, f'❌ تم رفض مجموعة "{group.name}".')
    return redirect('dashboard:pending_requests')

@staff_member_required
def approve_graduate(request, pk):
    graduate = get_object_or_404(Graduate, pk=pk)
    graduate.is_active = True
    graduate.is_verified = True
    graduate.save()
    
    # إشعار للخريج
    Notification.objects.create(
        recipient=graduate.user,
        title='✅ تم قبول تسجيلك',
        message=f'تم قبول طلب تسجيلك كخريج في منصة متابعة الخريجين.',
        notification_type='success',
        link=f'/graduates/{graduate.id}/'
    )
    
    messages.success(request, f'✅ تم قبول الخريج {graduate.user.get_full_name()} بنجاح.')
    return redirect('dashboard:pending_requests')


@staff_member_required
def approve_graduate(request, pk):
    graduate = get_object_or_404(Graduate, pk=pk)
    graduate.is_active = True
    graduate.is_verified = True
    graduate.save()
    
    # إشعار للخريج
    Notification.objects.create(
        recipient=graduate.user,
        title='✅ تم قبول تسجيلك',
        message=f'تم قبول طلب تسجيلك كخريج في منصة متابعة الخريجين.',
        notification_type='success',
        link=f'/graduates/{graduate.id}/'
    )
    
    messages.success(request, f'✅ تم قبول الخريج {graduate.user.get_full_name()} بنجاح.')
    return redirect('dashboard:pending_requests')


@login_required
def update_notification_preferences(request):
    try:
        graduate = request.user.graduate_profile
    except Graduate.DoesNotExist:
        messages.error(request, "لا يوجد ملف خريج مرتبط بحسابك.")
        return redirect('home')

    if request.method == 'POST':
        receive_email = request.POST.get('receive_email_notifications') == 'on'
        graduate.receive_email_notifications = receive_email
        graduate.save()
        messages.success(request, '✅ تم تحديث تفضيلات الإشعارات بنجاح.')
    return redirect('graduate_profile', pk=graduate.pk)