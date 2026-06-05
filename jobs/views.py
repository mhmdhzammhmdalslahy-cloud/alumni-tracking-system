from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from django.utils import timezone
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
from employers.models import Employer


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
        if self.request.user.is_authenticated and hasattr(self.request.user, 'graduate_profile'):
            context['has_applied'] = JobApplication.objects.filter(
                job=self.object,
                graduate=self.request.user.graduate_profile
            ).exists()
        return context


class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/job_form.html'
    success_url = reverse_lazy('job_list')  # هذا السطر مهم جداً

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


def apply_for_job(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if not hasattr(request.user, 'graduate_profile'):
        messages.error(request, 'يجب أن تكون مسجلاً كخريج للتقديم على الوظائف')
        return redirect('graduate_create')

    if JobApplication.objects.filter(job=job, graduate=request.user.graduate_profile).exists():
        messages.error(request, 'لقد تقدمت لهذه الوظيفة بالفعل')
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.graduate = request.user.graduate_profile
            application.save()
            messages.success(request, '✅ تم التقديم على الوظيفة بنجاح')
            return redirect('job_detail', pk=pk)
    else:
        form = JobApplicationForm()

    return render(request, 'jobs/job_apply.html', {'form': form, 'job': job})
def apply_for_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    if not hasattr(request.user, 'graduate_profile'):
        messages.error(request, 'يجب أن تكون مسجلاً كخريج للتقديم على الوظائف')
        return redirect('graduate_create')
    
    if JobApplication.objects.filter(job=job, graduate=request.user.graduate_profile).exists():
        messages.error(request, 'لقد تقدمت لهذه الوظيفة بالفعل')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.graduate = request.user.graduate_profile
            application.save()
            
            # حفظ تقييم الشركة إذا وجد
            company_rating = request.POST.get('company_rating')
            if company_rating and int(company_rating) > 0:
                from employers.models import CompanyReview
                CompanyReview.objects.create(
                    employer=job.employer,
                    graduate=request.user.graduate_profile,
                    rating=company_rating,
                    comment=f"تقييم تلقائي أثناء التقديم على وظيفة {job.title}"
                )
            
            messages.success(request, '✅ تم التقديم على الوظيفة بنجاح')
            return redirect('job_detail', pk=pk)
    else:
        form = JobApplicationForm()
    
    return render(request, 'jobs/job_apply.html', {'form': form, 'job': job})