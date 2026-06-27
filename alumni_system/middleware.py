from django.utils import translation

class ForceLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = request.COOKIES.get('django_language')
        print(f"🌐 Middleware reads: {language}")  # للتصحيح
        if language in ['ar', 'en']:
            translation.activate(language)
            request.LANGUAGE_CODE = language
        else:
            translation.activate('ar')
            request.LANGUAGE_CODE = 'ar'
        response = self.get_response(request)
        return response