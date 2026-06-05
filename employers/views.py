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
from graduates.models import Graduate  # ✅ أضف هذا السطر مهم جداً
import re


class EmployerListView(ListView):
    model = Employer
    template_name = 'employers/employer_list.html'
    context_object_name = 'employers'
    paginate_by = 12

    def get_queryset(self):
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
        context['total_companies'] = Employer.objects.filter(is_active=True).count()
        context['verified_companies'] = Employer.objects.filter(is_verified=True).count()
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
        
        # إضافة التقييمات للسياق
        from django.db.models import Avg
        avg_rating = self.object.reviews.aggregate(Avg('rating'))['rating__avg']
        context['avg_rating'] = round(avg_rating, 1) if avg_rating else 0
        context['reviews_count'] = self.object.reviews.count()
        
        print("=" * 50)
        print(f"🏢 شركة: {self.object.company_name}")
        print(f"📊 عدد الوظائف النشطة: {active_jobs.count()}")
        for job in active_jobs:
            print(f"  - {job.title} (ينتهي: {job.deadline})")
        print(f"📋 إجمالي الطلبات: {context['total_applications']}")
        print("=" * 50)
        return context


class EmployerCreateView(LoginRequiredMixin, CreateView):
    model = Employer
    form_class = EmployerForm
    template_name = 'employers/employer_form.html'
    success_url = reverse_lazy('employer_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, '✅ تم تسجيل الشركة بنجاح! سيتم مراجعة طلبك قريباً')
        return response


class EmployerUpdateView(LoginRequiredMixin, UpdateView):
    model = Employer
    form_class = EmployerForm
    template_name = 'employers/employer_form.html'
    success_url = reverse_lazy('employer_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '✅ تم تحديث بيانات الشركة بنجاح')
        return response


class EmployerDeleteView(LoginRequiredMixin, DeleteView):
    model = Employer
    success_url = reverse_lazy('employer_list')
    template_name = 'employers/employer_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        messages.success(request, '✅ تم حذف الشركة بنجاح')
        return super().delete(request, *args, **kwargs)


# ========== الدوال المساعدة (خارج الكلاسات) ==========

def verify_commercial_registration(commercial_registration):
    """التحقق التلقائي من صحة السجل التجاري"""
    if not re.match(r'^\d{8,12}$', commercial_registration):
        return False, "تنسيق السجل التجاري غير صحيح (يجب أن يكون 8-12 رقم)"
    return True, "✅ السجل التجاري صحيح"


def verify_employer(request, pk):
    employer = get_object_or_404(Employer, pk=pk)

    if request.method == 'POST':
        form = EmployerVerificationForm(request.POST, request.FILES)
        if form.is_valid():
            # التحقق من السجل التجاري تلقائياً
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


def accept_application(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if request.user == application.job.employer.user:
        application.status = 'accepted'
        application.save()
        messages.success(request, f'✅ تم قبول طلب {application.graduate.user.get_full_name()} بنجاح! سيتم التواصل معه قريباً.')
    return redirect('employer_profile', pk=application.job.employer.pk)


def reject_application(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if request.user == application.job.employer.user:
        application.status = 'rejected'
        application.save()
        messages.warning(request, f'📝 تم رفض طلب {application.graduate.user.get_full_name()}. نتمنى له التوفيق في فرص أخرى!')
    return redirect('employer_profile', pk=application.job.employer.pk)


def call_for_interview(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if request.user == application.job.employer.user:
        application.status = 'interview'
        application.save()
        messages.info(request, f'📅 تم تحديد مقابلة مع {application.graduate.user.get_full_name()}. سيتم إرسال التفاصيل عبر البريد الإلكتروني.')
    return redirect('employer_profile', pk=application.job.employer.pk)


def add_review(request, pk):
    employer = get_object_or_404(Employer, pk=pk)
    if request.method == 'POST' and hasattr(request.user, 'graduate_profile'):
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        # التحقق من وجود تقييم سابق
        existing_review = CompanyReview.objects.filter(employer=employer, graduate=request.user.graduate_profile).first()
        if existing_review:
            existing_review.rating = rating
            existing_review.comment = comment
            existing_review.save()
            messages.success(request, '✅ تم تحديث تقييمك بنجاح')
        else:
            CompanyReview.objects.create(
                employer=employer,
                graduate=request.user.graduate_profile,
                rating=rating,
                comment=comment
            )
            messages.success(request, '✅ تم إضافة تقييمك بنجاح')
    return redirect('employer_profile', pk=pk)


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
    
    return render(request, 'employers/search_graduates.html', {'graduates': queryset})


# إرسال إشعار واتساب (يتطلب API خارجي)
def send_whatsapp_notification(phone, message):
    # يمكن استخدام Twilio أو WATI أو GreenAPI
    pass

def accept_application_page(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if request.user != application.job.employer.user:
        messages.error(request, 'غير مصرح لك')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    if request.method == 'POST':
        # إجراءات القبول (إرسال عرض وظيفي، توقيع عقد، إلخ)
        offer_message = request.POST.get('offer_message', '')
        salary_offered = request.POST.get('salary_offered', '')
        
        application.status = 'accepted'
        application.notes = f"عرض وظيفي: {offer_message}\nالراتب المعروض: {salary_offered}"
        application.save()
        
        # إرسال إشعار للخريج
        messages.success(request, f'✅ تم قبول الطلب وإرسال العرض الوظيفي للخريج')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    return render(request, 'employers/accept_application.html', {'application': application})


def interview_application_page(request, app_id):
    application = get_object_or_404(JobApplication, id=app_id)
    if request.user != application.job.employer.user:
        messages.error(request, 'غير مصرح لك')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    if request.method == 'POST':
        interview_date = request.POST.get('interview_date')
        interview_link = request.POST.get('interview_link', '')
        interview_notes = request.POST.get('interview_notes', '')
        
        application.status = 'interview'
        application.interview_date = interview_date
        application.notes = f"موعد المقابلة: {interview_date}\nالرابط: {interview_link}\nملاحظات: {interview_notes}"
        application.save()
        
        messages.success(request, f'📅 تم تحديد المقابلة وإشعار الخريج')
        return redirect('employer_profile', pk=application.job.employer.pk)
    
    return render(request, 'employers/interview_application.html', {'application': application})