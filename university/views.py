from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import (
    UniversityNews, StudyMaterial, Job, Course, 
    Partner, AcademicCalendar
)
from itertools import chain
from operator import attrgetter

# ============================================================
# الصفحة الرئيسية (Hub)
# ============================================================
@login_required
def university_hub(request):
    # 1. جلب آخر 5 أخبار للـ Carousel
    latest_news = UniversityNews.objects.filter(
        is_published=True
    ).order_by('-published_at')[:5]

    # 2. جلب آخر 5 مواد دراسية للمكتبة
    latest_materials = StudyMaterial.objects.all().order_by('-created_at')[:5]

    # 3. جلب آخر 3 وظائف نشطة
    latest_jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:3]

    # 4. جلب آخر 3 دورات نشطة
    latest_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]

    # 5. جلب الشركاء النشطين
    partners = Partner.objects.filter(is_active=True).order_by('order')[:6]

    # 6. جلب أحداث التقويم القادمة
    upcoming_events = AcademicCalendar.objects.filter(
        is_active=True
    ).order_by('date')[:5]

    # 7. عدادات القائمة العلوية
    news_count = UniversityNews.objects.filter(is_published=True).count()
    courses_count = Course.objects.filter(is_active=True).count()

    # ============================================================
    # ✅ الجزء المُعدّل: دمج العناصر في قائمة واحدة بأمان
    # ============================================================
    feed_items = []

    # إضافة العناصر من كل قائمة إذا كانت موجودة
    for item in latest_news:
        feed_items.append(item)
    for item in latest_jobs:
        feed_items.append(item)
    for item in latest_courses:
        feed_items.append(item)

    # ترتيب القائمة حسب تاريخ الإنشاء (الأحدث أولاً)
    # نستخدم دالة lambda للتعامل مع الكائنات المختلفة
    feed_items.sort(
        key=lambda x: getattr(x, 'created_at', getattr(x, 'published_at', None)),
        reverse=True
    )

    # أخذ أول 6 عناصر فقط
    feed_items = feed_items[:6]

    # ============================================================

    context = {
        'feed_items': feed_items,
        'latest_materials': latest_materials,
        'latest_jobs': latest_jobs,
        'latest_courses': latest_courses,
        'partners': partners,
        'upcoming_events': upcoming_events,
        'news_count': news_count,
        'courses_count': courses_count,
    }
    return render(request, 'university/hub.html', context)
# ============================================================
# صفحات الأخبار والإعلانات
# ============================================================
def news_list(request):
    """عرض جميع الأخبار والإعلانات مع تصفية حسب التصنيف"""
    category = request.GET.get('category', '')
    news = UniversityNews.objects.filter(is_published=True)
    
    if category:
        news = news.filter(category=category)
    
    categories = UniversityNews.CATEGORY_CHOICES
    context = {
        'news': news,
        'categories': categories,
        'selected_category': category,
    }
    return render(request, 'university/news_list.html', context)

def news_detail(request, pk):
    """عرض تفاصيل خبر معين"""
    news_item = get_object_or_404(UniversityNews, pk=pk, is_published=True)
    return render(request, 'university/news_detail.html', {'news_item': news_item})

# ============================================================
# التقويم الأكاديمي
# ============================================================
def calendar_list(request):
    """عرض التقويم الأكاديمي"""
    events = AcademicCalendar.objects.filter(is_active=True).order_by('date')
    return render(request, 'university/calendar_list.html', {'events': events})

# ============================================================
# المكتبة الرقمية
# ============================================================
def digital_library(request):
    """عرض المواد الدراسية في المكتبة الرقمية"""
    materials = StudyMaterial.objects.all().order_by('-created_at')
    return render(request, 'university/digital_library.html', {'materials': materials})

def study_material_detail(request, pk):
    """عرض تفاصيل مادة دراسية"""
    material = get_object_or_404(StudyMaterial, pk=pk)
    return render(request, 'university/study_material_detail.html', {'material': material})

# ============================================================
# مركز التوظيف
# ============================================================
def career_center(request):
    """عرض جميع الوظائف المتاحة"""
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'university/career_center.html', {'jobs': jobs})

def job_detail(request, pk):
    """عرض تفاصيل وظيفة معينة"""
    job = get_object_or_404(Job, pk=pk, is_active=True)
    return render(request, 'university/job_detail.html', {'job': job})

def job_list(request):
    """عرض قائمة الوظائف (بديل لـ career_center)"""
    return career_center(request)

# ============================================================
# التعليم المستمر (الدورات)
# ============================================================
def continuing_education(request):
    """عرض جميع الدورات المتاحة في التعليم المستمر"""
    courses = Course.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'university/continuing_education.html', {'courses': courses})

def course_detail(request, pk):
    """عرض تفاصيل دورة معينة"""
    course = get_object_or_404(Course, pk=pk, is_active=True)
    return render(request, 'university/course_detail.html', {'course': course})

def course_list(request):
    """عرض قائمة الدورات (بديل لـ continuing_education)"""
    return continuing_education(request)

# ============================================================
# تحليل سوق العمل
# ============================================================
def market_analysis(request):
    """عرض تحليل سوق العمل وإحصائياته"""
    # إحصائيات سريعة
    total_jobs = Job.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_news = UniversityNews.objects.filter(is_published=True).count()
    
    context = {
        'total_jobs': total_jobs,
        'total_courses': total_courses,
        'total_news': total_news,
    }
    return render(request, 'university/market_analysis.html', context)

# ============================================================
# الشركاء
# ============================================================
def partner_list(request):
    """عرض قائمة الشركاء"""
    partners = Partner.objects.filter(is_active=True).order_by('order')
    return render(request, 'university/partner_list.html', {'partners': partners})