from django.shortcuts import render
from django.db.models import Q
from graduates.models import Graduate
from jobs.models import Job
from django.utils import translation
from django.shortcuts import redirect

def search_all(request):
    query = request.GET.get('q', '').strip()
    print(f"🔍 Searching for: '{query}'")
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
        
        print(f"📊 Found graduates: {graduates.count()}, jobs: {jobs.count()}")
    
    return render(request, 'search_results.html', {
        'graduates': graduates,
        'jobs': jobs,
        'query': query
    })

def set_language(request):
    language_code = request.GET.get('language')
    print(f"🔥 set_language called with: {language_code}")
    
    if language_code in ['ar', 'en']:
        translation.activate(language_code)
        request.session['django_language'] = language_code
        
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('django_language', language_code, max_age=60*60*24*365)
        
        print(f"✅ Language set to: {language_code}")
        return response
    
    print("❌ Invalid language code")
    return redirect('/')