from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from dashboard.models import Survey, SurveyResponse
from .models import Graduate, WorkExperience, Skill, Certification, AcademicProject
from .forms import GraduateForm, VerificationForm
from .filters import GraduateFilter
from .verification import verify_university_id
from dashboard.models import SuccessStory
from groups.models import Group

# ============================================================
# ✅ ديكور مخصص للتحقق من صلاحيات المشرف
# ============================================================
def is_admin(user):
    """التحقق من أن المستخدم لديه صلاحيات إدارية"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    try:
        if hasattr(user, 'admin_profile') and user.admin_profile.is_active:
            return user.admin_profile.admin_level in ['super_admin', 'admin']
    except:
        pass
    return False

def admin_required(view_func):
    """ديكور للتحقق من صلاحيات المشرف قبل تنفيذ الـ View"""
    def wrapper(request, *args, **kwargs):
        if is_admin(request.user):
            return view_func(request, *args, **kwargs)
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, "غير مصرح لك بالوصول إلى هذه الصفحة.")
        return redirect('home')
    return wrapper


class GraduateListView(ListView):
    model = Graduate
    template_name = 'graduates/graduate_list.html'
    context_object_name = 'graduates'
    paginate_by = 12

    def get_queryset(self):
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

class GraduateProfileView(DetailView):
    model = Graduate
    template_name = 'graduates/graduate_profile.html'
    context_object_name = 'graduate'

    def get_object(self):
        obj = super().get_object()
        obj.profile_views += 1
        obj.save()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        answered_ids = SurveyResponse.objects.filter(graduate=self.object).values_list('survey_id', flat=True)
        available_surveys = Survey.objects.filter(is_active=True, is_published=True).exclude(id__in=answered_ids)
        context['available_surveys'] = available_surveys
        
        return context

class GraduateCreateView(CreateView):
    model = Graduate
    form_class = GraduateForm
    template_name = 'graduates/graduate_form.html'
    success_url = reverse_lazy('graduate_list')

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
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
        'latest_graduates': Graduate.objects.filter(is_verified=True).order_by('-created_at')[:6],
        'latest_jobs': Job.objects.filter(is_active=True).order_by('-created_at')[:6],
        'success_stories': SuccessStory.objects.filter(status='approved', is_active=True)[:3],
    }
    return render(request, 'index.html', context)


from django.contrib.auth.decorators import login_required

@login_required
def update_notification_preferences(request):
    if request.method == 'POST':
        if not hasattr(request.user, 'graduate_profile'):
            messages.error(request, '⚠️ يرجى إكمال ملفك الشخصي أولاً.')
            return redirect('graduate_create')
        
        graduate = request.user.graduate_profile
        receive_email = request.POST.get('receive_email_notifications') == 'on'
        graduate.receive_email_notifications = receive_email
        graduate.save()
        
        messages.success(request, '✅ تم تحديث تفضيلات الإشعارات بنجاح!')
        return redirect('graduate_profile', pk=graduate.pk)
    
    if hasattr(request.user, 'graduate_profile'):
        return redirect('graduate_profile', pk=request.user.graduate_profile.pk)
    return redirect('graduate_create')


@admin_required
def delete_group(request, pk):
    """حذف مجموعة"""
    group = get_object_or_404(Group, pk=pk)
    group_name = group.name
    group.delete()
    messages.success(request, f'✅ تم حذف المجموعة "{group_name}" بنجاح.')
    return redirect('dashboard:admin_dashboard')


@admin_required
def delete_success_story(request, pk):
    """حذف قصة نجاح"""
    story = get_object_or_404(SuccessStory, pk=pk)
    story_title = story.title
    story.delete()
    messages.success(request, f'✅ تم حذف القصة "{story_title}" بنجاح.')
    return redirect('dashboard:admin_dashboard')