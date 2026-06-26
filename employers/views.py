from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from .models import Employer, EmployerVerificationRequest, CompanyReview
from .forms import EmployerForm, EmployerVerificationForm
from jobs.models import Job, JobApplication
from graduates.models import Graduate
from dashboard.models import Notification
import re
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from dashboard.decorators import employer_required


# ========== قائمة وعرض الشركات ==========

class EmployerListView(ListView):
    model = Employer
    template_name = 'employers/employer_list.html'
    context_object_name = 'employers'
    paginate_by = 12

    def get_queryset(self):
        # ✅ فقط الشركات الموثقة
        queryset = Employer.objects.filter(is_active=True, is_verified=True)
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search) |
                Q(industry__icontains=search) |
                Q(headquarters__icontains=search)
            )
        industry = self.request.GET.get('industry', '')
        if industry:
            queryset = queryset.filter(industry=industry)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_companies'] = Employer.objects.filter(is_active=True, is_verified=True).count()
        context['verified_companies'] = Employer.objects.filter(is_verified=True).count()
        
        # ✅ أعلى الشركات توظيفاً
        from django.db.models import Count, Q
        context['top_employers'] = Employer.objects.filter(
            is_active=True, is_verified=True
        ).annotate(
            job_count=Count('jobs', filter=Q(jobs__is_active=True))
        ).filter(job_count__gt=0).order_by('-job_count')[:5]
        
        return context



class EmployerDetailView(DetailView):
    model = Employer
    template_name = 'employers/employer_profile.html'
    context_object_name = 'employer'

    def get_object(self):
        obj = super().get_object()
        obj.views_count += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_jobs = self.object.jobs.filter(is_active=True, deadline__gte=timezone.now())
        context['active_jobs'] = active_jobs
        context['total_applications'] = JobApplication.objects.filter(job__employer=self.object).count()
        
        from django.db.models import Avg
        avg_rating = self.object.reviews.aggregate(Avg('rating'))['rating__avg']
        context['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        context['reviews_count'] = self.object.reviews.count()
        return context


# ========== إنشاء وتعديل وحذف الشركات ==========

class EmployerCreateView(LoginRequiredMixin, CreateView):
    model = Employer
    form_class = EmployerForm
    template_name = 'employers/employer_form.html'
    success_url = reverse_lazy('employer_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # ✅ الشركة الجديدة غير موثقة حتى يوافق عليها المشرف
        form.instance.is_verified = False
        response = super().form_valid(form)
        messages.success(self.request, '✅ تم تسجيل الشركة بنجاح! سيتم مراجعة طلبك من قبل الإدارة.')
        return response


class EmployerUpdateView(LoginRequiredMixin, UpdateView):
    model = Employer
    form_class = EmployerForm
    template_name = 'employers/employer_form.html'
    success_url = reverse_lazy('employer_list')

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employer_profile'):
            messages.error(request, '⚠️ يجب أن تكون مسجلاً كشركة لتعديل الملف.')
            return redirect('employer_list')
        
        obj = get_object_or_404(Employer, pk=kwargs['pk'])
        if obj.user != request.user:
            messages.error(request, '⚠️ ليس لديك صلاحية لتعديل ملف هذه الشركة.')
            return redirect('employer_list')
        
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employer_profile'):
            messages.error(request, '⚠️ يجب أن تكون مسجلاً كشركة لتعديل الملف.')
            return redirect('employer_list')
        
        obj = get_object_or_404(Employer, pk=kwargs['pk'])
        if obj.user != request.user:
            messages.error(request, '⚠️ ليس لديك صلاحية لتعديل ملف هذه الشركة.')
            return redirect('employer_list')
        
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '✅ تم تحديث بيانات الشركة بنجاح!')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'❌ خطأ في حقل {field}: {error}')
        return super().form_invalid(form)


class EmployerDeleteView(LoginRequiredMixin, DeleteView):
    model = Employer
    success_url = reverse_lazy('employer_list')
    template_name = 'employers/employer_confirm_delete.html'

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employer_profile'):
            messages.error(request, '⚠️ يجب أن تكون مسجلاً كشركة لحذف الملف.')
            return redirect('employer_create')
        
        obj = get_object_or_404(Employer, pk=kwargs['pk'])
        if obj.user != request.user:
            messages.error(request, '⚠️ ليس لديك صلاحية لحذف ملف هذه الشركة.')
            return redirect('employer_list')
        
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


# ========== دوال التوثيق والتحقق (مع إنشاء تلقائي للطلب) ==========

def verify_commercial_registration(commercial_registration):
    """التحقق التلقائي من صحة السجل التجاري"""
    if not re.match(r'^\d{8,12}$', commercial_registration):
        return False, "تنسيق السجل التجاري غير صحيح (يجب أن يكون 8-12 رقم)"
    return True, "✅ السجل التجاري صحيح"


def verify_employer(request, pk):
    employer = get_object_or_404(Employer, pk=pk)
    
    # محاولة جلب طلب توثيق معلق
    verification = EmployerVerificationRequest.objects.filter(employer=employer, status='pending').first()
    
    # ✅ إذا لم يكن هناك طلب معلق، قم بإنشائه تلقائياً
    if not verification:
        verification = EmployerVerificationRequest.objects.create(
            employer=employer,
            commercial_registration_file='',  # يمكن تركه فارغاً أو تعيين قيمة افتراضية
            status='pending'
        )
        messages.info(request, f'📝 تم إنشاء طلب توثيق تلقائي للشركة {employer.company_name}')
        return redirect('dashboard:verify_employer', pk=employer.pk)

    if request.method == 'POST':
        form = EmployerVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            if employer.commercial_registration:
                is_valid, msg = verify_commercial_registration(employer.commercial_registration)
                if not is_valid:
                    messages.error(request, f'❌ {msg}')
                    return redirect('employer_profile', pk=employer.pk)
            
            verification = form.save(commit=False)
            verification.employer = employer
            verification.save()
            messages.success(request, '✅ تم إرسال طلب التوثيق بنجاح، سيتم مراجعته قريباً')
            return redirect('employer_profile', pk=employer.pk)
    else:
        form = EmployerVerificationForm()

    return render(request, 'employers/employer_verify.html', {'form': form, 'employer': employer})


# ========== إدارة طلبات التوظيف (القبول - الرفض - المقابلة) ==========
def accept_application(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    
    if request.user != application.job.employer.user:
        messages.error(request, '⚠️ غير مصرح لك بالتعامل مع هذا الطلب.')
        return redirect('employer_list')
    
    application.status = 'accepted'
    application.save()
    
    # ✅ إشعار في التطبيق
    Notification.objects.create(
        recipient=application.graduate.user,
        title='🎉 تم قبول طلبك الوظيفي',
        message=f'قامت شركة {application.job.employer.company_name} بقبول طلبك لوظيفة {application.job.title}.',
        link=f'/jobs/{application.job.id}/'
    )
    
    # ✅ إرسال بريد إلكتروني ترحيبي للخريج
    subject = f'🎉 تهانينا! تم قبول طلبك لوظيفة {application.job.title}'
    html_message = render_to_string('emails/application_accepted.html', {
        'graduate': application.graduate,
        'job': application.job,
        'company': application.job.employer,
    })
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [application.graduate.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    # ✅ إرسال بريد إلكتروني للشركة (تأكيد)
    send_mail(
        f'✅ تم قبول طلب {application.graduate.user.get_full_name()}',
        f'تم قبول طلب الخريج {application.graduate.user.get_full_name()} لوظيفة {application.job.title}.',
        settings.DEFAULT_FROM_EMAIL,
        [application.job.employer.email],
        fail_silently=True,
    )
    
    messages.success(request, f'🎉 تم قبول طلب {application.graduate.user.get_full_name()} بنجاح! وتم إرسال بريد ترحيبي.')
    return redirect('employer_profile', pk=application.job.employer.pk)

def reject_application(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    
    if request.user != application.job.employer.user:
        messages.error(request, '⚠️ غير مصرح لك بالتعامل مع هذا الطلب.')
        return redirect('employer_list')
    
    application.status = 'rejected'
    application.save()
    
    # ✅ إشعار في التطبيق
    Notification.objects.create(
        recipient=application.graduate.user,
        title='📝 تحديث بخصوص طلبك الوظيفي',
        message=f'نأسف لإبلاغك بأن طلبك لوظيفة {application.job.title} لم يتم قبوله في هذه المرحلة. نتمنى لك التوفيق.',
        link=f'/jobs/{application.job.id}/'
    )
    
    # ✅ إرسال بريد إلكتروني للخريج
    subject = f'📝 تحديث بخصوص طلبك لوظيفة {application.job.title}'
    html_message = render_to_string('emails/application_rejected.html', {
        'graduate': application.graduate,
        'job': application.job,
        'company': application.job.employer,
    })
    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [application.graduate.user.email],
        html_message=html_message,
        fail_silently=False,
    )
    
    messages.warning(request, f'📝 تم رفض طلب {application.graduate.user.get_full_name()}. تم إرسال إشعار بالرفض.')
    return redirect('employer_profile', pk=application.job.employer.pk)

def call_for_interview(request, app_id):
    """اختصار سريع لتحديد مقابلة (يعيد التوجيه إلى صفحة تحديد الموعد)"""
    return interview_application_page(request, app_id)

def accept_application_page(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    
    if request.user != application.job.employer.user:
        messages.error(request, '⚠️ غير مصرح لك بالتعامل مع هذا الطلب.')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    if request.method == 'POST':
        offer_message = request.POST.get('offer_message', '')
        salary_offered = request.POST.get('salary_offered', '')
        
        application.status = 'accepted'
        application.notes = f"عرض وظيفي: {offer_message}\nالراتب المعروض: {salary_offered}"
        application.save()
        
        Notification.objects.create(
            recipient=application.graduate.user,
            title='🎉 تم قبول طلبك الوظيفي',
            message=f'قامت شركة {application.job.employer.company_name} بقبول طلبك لوظيفة {application.job.title}.',
            link=f'/jobs/{application.job.id}/'
        )
        
        messages.success(request, '✅ تم قبول الطلب وإرسال العرض الوظيفي للخريج')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    return render(request, 'employers/accept_application.html', {'application': application})

def interview_application_page(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    
    if request.user != application.job.employer.user:
        messages.error(request, '⚠️ غير مصرح لك بالتعامل مع هذا الطلب.')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    if request.method == 'POST':
        interview_date = request.POST.get('interview_date')
        interview_link = request.POST.get('interview_link', '')
        interview_notes = request.POST.get('interview_notes', '')
        
        application.status = 'interview'
        application.interview_date = interview_date
        application.notes = f"موعد المقابلة: {interview_date}\nالرابط: {interview_link}\nملاحظات: {interview_notes}"
        application.save()
        
        # ✅ إشعار في التطبيق
        Notification.objects.create(
            recipient=application.graduate.user,
            title='📅 دعوة لإجراء مقابلة',
            message=f'تمت دعوتك لإجراء مقابلة مع شركة {application.job.employer.company_name} بتاريخ {interview_date}.',
            link=f'/jobs/{application.job.id}/'
        )
        
        # ✅ إرسال بريد إلكتروني للخريج
        subject = f'📅 دعوة لمقابلة شخصية - {application.job.title}'
        html_message = render_to_string('emails/interview_invitation.html', {
            'graduate': application.graduate,
            'job': application.job,
            'company': application.job.employer,
            'interview_date': interview_date,
            'interview_link': interview_link,
            'interview_notes': interview_notes,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [application.graduate.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        messages.success(request, f'📅 تم تحديد المقابلة مع {application.graduate.user.get_full_name()} وإشعاره عبر البريد الإلكتروني.')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    return render(request, 'employers/interview_application.html', {'application': application})

# ========== إضافة تقييم للشركة ==========

from django.contrib.auth.decorators import login_required

@login_required
def add_review(request, pk):
    """إضافة أو تحديث تقييم للشركة"""
    employer = get_object_or_404(Employer, pk=pk)
    
    # ✅ التحقق من أن المستخدم خريج
    if not hasattr(request.user, 'graduate_profile'):
        messages.error(request, '⚠️ يجب أن تكون خريجاً لتقييم الشركات.')
        return redirect('employer_profile', pk=pk)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()
        
        # ✅ التحقق من صحة التقييم
        if not rating or not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
            messages.error(request, '⚠️ الرجاء اختيار تقييم من 1 إلى 5 نجوم.')
            return redirect('employer_profile', pk=pk)
        
        # ✅ حفظ أو تحديث التقييم
        review, created = CompanyReview.objects.get_or_create(
            employer=employer,
            graduate=request.user.graduate_profile,
            defaults={'rating': rating, 'comment': comment}
        )
        if not created:
            review.rating = rating
            review.comment = comment
            review.save()
            messages.success(request, '✅ تم تحديث تقييمك للشركة بنجاح.')
        else:
            messages.success(request, '✅ تم إضافة تقييمك للشركة بنجاح.')
        
        # ✅ إشعار للشركة
        Notification.objects.create(
            recipient=employer.user,
            title='⭐ تقييم جديد لشركتك',
            message=f'قام {request.user.get_full_name()} بتقييم شركتك بـ {rating} نجوم.',
            link=f'/employers/{employer.pk}/'
        )
        
        return redirect('employer_profile', pk=pk)
    
    return redirect('employer_profile', pk=pk)

# ========== البحث عن الخريجين ==========

def search_graduates(request):
    queryset = Graduate.objects.filter(is_verified=True)
    name = request.GET.get('name', '')
    if name:
        queryset = queryset.filter(
            Q(user__first_name__icontains=name) | 
            Q(user__last_name__icontains=name)
        )
    major = request.GET.get('major', '')
    if major:
        queryset = queryset.filter(major__icontains=major)
    skill = request.GET.get('skill', '')
    if skill:
        queryset = queryset.filter(skills__name__icontains=skill)
    city = request.GET.get('city', '')
    if city and city != 'جميع المدن':
        queryset = queryset.filter(address__icontains=city)
    year = request.GET.get('year', '')
    if year and year != 'جميع السنوات':
        
        queryset = queryset.filter(graduation_year=year)
    
    return render(request, 'graduates/graduate_list.html', {'graduates': queryset})