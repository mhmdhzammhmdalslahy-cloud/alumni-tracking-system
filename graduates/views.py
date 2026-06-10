from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Graduate, WorkExperience, Skill, Certification, AcademicProject
from .forms import GraduateForm, VerificationForm
from .filters import GraduateFilter
from .verification import verify_university_id
from dashboard.models import SuccessStory


class GraduateListView(ListView):
    model = Graduate
    template_name = 'graduates/graduate_list.html'
    context_object_name = 'graduates'
    paginate_by = 12

    def get_queryset(self):
        queryset = Graduate.objects.all().order_by('-created_at')

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(major__icontains=search_query)
            )

        major = self.request.GET.get('major', '')
        if major:
            queryset = queryset.filter(major__icontains=major)

        year = self.request.GET.get('year', '')
        if year:
            queryset = queryset.filter(graduation_year=year)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['working_count'] = Graduate.objects.filter(current_job_status='working').count()
        context['total_count'] = Graduate.objects.count()
        return context


class GraduateProfileView(DetailView):
    model = Graduate
    template_name = 'graduates/graduate_profile.html'
    context_object_name = 'graduate'

    def get_object(self):
        obj = super().get_object()
        obj.profile_views += 1
        obj.save()
        return obj


class GraduateCreateView(CreateView):
    model = Graduate
    form_class = GraduateForm
    template_name = 'graduates/graduate_form.html'
    success_url = reverse_lazy('graduate_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            response = super().form_valid(form)
            messages.success(self.request, '✅ تم إضافة الخريج بنجاح!')
            return response
        else:
            messages.warning(self.request, '⚠️ يرجى تسجيل الدخول أولاً')
            return redirect('login')

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'❌ خطأ في حقل {field}: {error}')
        return super().form_invalid(form)


class GraduateUpdateView(LoginRequiredMixin, UpdateView):
    model = Graduate
    form_class = GraduateForm
    template_name = 'graduates/graduate_form.html'
    success_url = reverse_lazy('graduate_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '✅ تم تحديث بيانات الخريج بنجاح!')
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'❌ خطأ في حقل {field}: {error}')
        return super().form_invalid(form)


class GraduateDeleteView(LoginRequiredMixin, DeleteView):
    model = Graduate
    success_url = reverse_lazy('graduate_list')
    template_name = 'graduates/graduate_confirm_delete.html'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


def verify_graduate(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            university_id = form.cleaned_data['university_id']
            graduation_year = form.cleaned_data['graduation_year']

            is_valid, message = verify_university_id(university_id, graduation_year)
            if is_valid:
                messages.success(request, f'✅ {message}')
                return redirect('graduate_create')
            else:
                messages.error(request, f'❌ {message}')
        else:
            messages.error(request, '❌ يرجى تعبئة جميع الحقول بشكل صحيح')
    else:
        form = VerificationForm()

    return render(request, 'graduates/graduate_verify.html', {'form': form})


def search_graduates(request):
    query = request.GET.get('q', '')
    if query:
        graduates = Graduate.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(major__icontains=query)
        )
        messages.info(request, f'🔍 تم العثور على {graduates.count()} خريج')
    else:
        graduates = Graduate.objects.none()

    return render(request, 'graduates/graduate_list.html', {'graduates': graduates})

def home(request):
    from graduates.models import Graduate
    from employers.models import Employer
    from jobs.models import Job
    from dashboard.models import SuccessStory

    total_graduates = Graduate.objects.count()
    total_employers = Employer.objects.count()
    total_jobs = Job.objects.filter(is_active=True).count()

    # حساب نسبة التوظيف
    working_graduates = Graduate.objects.filter(current_job_status='working').count()
    employment_rate = round((working_graduates / total_graduates) * 100) if total_graduates > 0 else 0

    context = {
        'total_graduates': total_graduates,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'employment_rate': employment_rate,
        'latest_graduates': Graduate.objects.all().order_by('-created_at')[:6],
        'latest_jobs': Job.objects.filter(is_active=True).order_by('-created_at')[:6],
        'success_stories': SuccessStory.objects.filter(status='approved', is_active=True)[:3],
    }
    return render(request, 'index.html', context)