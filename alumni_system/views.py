from django.shortcuts import render
from django.db.models import Q
from graduates.models import Graduate
from jobs.models import Job
def search_all(request):
    query = request.GET.get('q', '').strip()
    print(f"🔍 Searching for: '{query}'")  # تأكد من ظهورها في terminal
    graduates = []
    jobs = []
    if query:
        graduates = Graduate.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(major__icontains=query)
        )[:10]
        jobs = Job.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(employer__company_name__icontains=query)
        ).filter(is_active=True)[:10]
        print(f"📊 Found graduates: {graduates.count()}, jobs: {jobs.count()}")  # تحقق
    return render(request, 'search_results.html', {'graduates': graduates, 'jobs': jobs, 'query': query})