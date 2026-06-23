from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
from employers.models import Employer, CompanyReview
from dashboard.models import Notification


class JobListView(ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True, deadline__gte=timezone.now())

        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(location__icontains=search) |
                Q(required_skills__icontains=search) |
                Q(employer__company_name__icontains=search)
            )

        job_type = self.request.GET.get('type', '')
        if job_type:
            queryset = queryset.filter(job_type=job_type)

        location = self.request.GET.get('location', '')
        if location:
            queryset = queryset.filter(location__icontains=location)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_jobs'] = Job.objects.filter(is_active=True).count()
        return context


class JobDetailView(DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_object(self):
        obj = super().get_object()
        obj.views_count += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['has_applied'] = False
        context['application_status'] = None
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'graduate_profile'):
            application = JobApplication.objects.filter(
                job=self.object,
                graduate=self.request.user.graduate_profile
            ).first()
            
            if application:
                context['has_applied'] = True
                context['application_status'] = application.status
                context['application'] = application
        
        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job_list')

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employer_profile'):
            messages.error(request, 'يجب أن تكون مسجلاً كشركة لنشر وظيفة')
            return redirect('employer_create')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.employer = self.request.user.employer_profile
        messages.success(self.request, '✅ تم نشر الوظيفة بنجاح')
        return super().form_valid(form)


class JobUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job_list')

    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer.user

    def form_valid(self, form):
        messages.success(self.request, '✅ تم تحديث الوظيفة بنجاح')
        return super().form_valid(form)


class JobDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Job
    success_url = reverse_lazy('job_list')
    template_name = 'jobs/job_confirm_delete.html'

    def test_func(self):
        job = self.get_object()
        return self.request.user == job.employer.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, '✅ تم حذف الوظيفة بنجاح')
        return super().delete(request, *args, **kwargs)


# ============================================================
# ====== التقديم على الوظيفة (النسخة المطورة) ======
# ============================================================
def apply_for_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    # ✅ التحقق من أن المستخدم خريج
    if not hasattr(request.user, 'graduate_profile'):
        messages.error(request, 'يجب أن تكون مسجلاً كخريج للتقديم على الوظائف')
        return redirect('graduate_create')
    
    # ✅ التحقق من عدم التقديم مسبقاً
    if JobApplication.objects.filter(job=job, graduate=request.user.graduate_profile).exists():
        messages.error(request, 'لقد تقدمت لهذه الوظيفة بالفعل')
        # ✅ تم التعديل: إضافة 'jobs:'
        return redirect('jobs:job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.graduate = request.user.graduate_profile
            application.save()
            
            # ✅ حفظ تقييم الشركة (استخدام get_or_create لتجنب التكرار)
            company_rating = request.POST.get('company_rating')
            if company_rating and int(company_rating) > 0:
                # ✅ تم التعديل: استخدام get_or_create بدلاً من create
                review, created = CompanyReview.objects.get_or_create(
                    employer=job.employer,
                    graduate=request.user.graduate_profile,
                    defaults={
                        'rating': company_rating,
                        'comment': f"تقييم تلقائي أثناء التقديم على وظيفة {job.title}"
                    }
                )
                if not created:
                    review.rating = company_rating
                    review.comment = f"تقييم تلقائي أثناء التقديم على وظيفة {job.title}"
                    review.save()
            
            # ✅ إشعار للشركة
            Notification.objects.create(
                recipient=job.employer.user,
                title='📩 طلب توظيف جديد',
                message=f'قام {request.user.get_full_name()} بالتقديم على وظيفة {job.title}',
                link=f'/employers/application/{application.id}/'
            )
            
            # ✅ إشعار للخريج (تأكيد التقديم)
            Notification.objects.create(
                recipient=request.user,
                title='✅ تم تقديم طلبك بنجاح',
                message=f'تم تقديم طلبك لوظيفة {job.title} في شركة {job.employer.company_name}',
                link=f'/jobs/{job.pk}/'
            )
            
            # ✅ إرسال بريد إلكتروني تأكيدي للخريج
            subject = f'✅ تأكيد تقديم طلبك لوظيفة {job.title}'
            html_message = render_to_string('emails/application_submitted.html', {
                'graduate': request.user.graduate_profile,
                'job': job,
                'company': job.employer,
            })
            send_mail(
                subject,
                strip_tags(html_message),
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            messages.success(request, '✅ تم التقديم على الوظيفة بنجاح! سيتم إشعارك عند مراجعة طلبك.')
            # ✅ تم التعديل: إضافة 'jobs:'
            return redirect('jobs:job_detail', pk=pk)
    else:
        # ✅ تم التعديل: إصلاح الخطأ الإملائي
        form = JobApplicationForm()
    
    return render(request, 'jobs/job_apply.html', {'form': form, 'job': job})