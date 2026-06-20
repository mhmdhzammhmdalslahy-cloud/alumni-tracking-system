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
        # ✅ فقط الخريجين الموثقين (is_verified=True)
        queryset = Graduate.objects.filter(is_verified=True).order_by('-created_at')

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
        # ✅ فقط الخريجين الموثقين في الإحصائيات
        context['working_count'] = Graduate.objects.filter(is_verified=True, current_job_status='working').count()
        context['total_count'] = Graduate.objects.filter(is_verified=True).count()
        return context


class GraduateProfileView(DetailView):
    model = Graduate
    template_name = 'graduates/graduate_profile.html'
    context_object_name = 'graduate'

    def get_object(self):
        obj = super().get_object()
        # ✅ يمكن عرض الملف حتى لو غير موثق (لكن يمكن منع الوصول إذا أردت)
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
            # ✅ الخريج الجديد يكون غير موثق حتى يوافق عليه المشرف
            form.instance.is_verified = False
            response = super().form_valid(form)
            messages.success(self.request, '✅ تم إضافة الخريج بنجاح! سيتم مراجعة طلبك من قبل الإدارة.')
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

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'graduate_profile'):
            messages.error(request, '⚠️ يجب أن تكون خريجاً مسجلاً لتعديل الملف.')
            return redirect('graduate_create')
        
        obj = get_object_or_404(Graduate, pk=kwargs['pk'])
        if obj.user != request.user:
            messages.error(request, '⚠️ ليس لديك صلاحية لتعديل هذا الملف. يمكنك فقط تعديل ملفك الشخصي.')
            return redirect('graduate_list')
        
        return super().dispatch(request, *args, **kwargs)

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

    def get_object(self, queryset=None):
        obj = get_object_or_404(Graduate, pk=self.kwargs['pk'])
        
        if obj.user != self.request.user:
            messages.error(self.request, '⚠️ ليس لديك صلاحية لحذف هذا الملف. يمكنك فقط حذف ملفك الشخصي.')
            return redirect('graduate_list')
        
        return obj

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'graduate_profile'):
            messages.error(request, '⚠️ يجب أن تكون خريجاً مسجلاً لحذف الملف.')
            return redirect('graduate_create')
        return super().dispatch(request, *args, **kwargs)

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
        # ✅ فقط الخريجين الموثقين في نتائج البحث
        graduates = Graduate.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(major__icontains=query),
            is_verified=True
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

    # ✅ إحصائيات تعتمد فقط على الخريجين الموثقين
    total_graduates = Graduate.objects.filter(is_verified=True).count()
    total_employers = Employer.objects.filter(is_verified=True).count()
    total_jobs = Job.objects.filter(is_active=True).count()

    working_graduates = Graduate.objects.filter(is_verified=True, current_job_status='working').count()
    employment_rate = round((working_graduates / total_graduates) * 100) if total_graduates > 0 else 0

    context = {
        'total_graduates': total_graduates,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'employment_rate': employment_rate,
        # ✅ أحدث الخريجين الموثقين فقط
        'latest_graduates': Graduate.objects.filter(is_verified=True).order_by('-created_at')[:6],
        'latest_jobs': Job.objects.filter(is_active=True).order_by('-created_at')[:6],
        'success_stories': SuccessStory.objects.filter(status='approved', is_active=True)[:3],
    }
    return render(request, 'index.html', context)