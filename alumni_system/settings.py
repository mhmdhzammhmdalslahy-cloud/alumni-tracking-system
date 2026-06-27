import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# تحميل المتغيرات من ملف .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-this')

DEBUG = True

ALLOWED_HOSTS = ['*']


# ============================================================
# ========== التطبيقات المثبتة ==========
# ============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'whitenoise.runserver_nostatic',
    
    # Celery & WebPush (معلقين مؤقتاً)
    # 'django_celery_beat',
    # 'webpush',
    
    # Local apps
    'accounts',
    'graduates',
    'employers',
    'jobs',
    'surveys',
    'dashboard',
    'groups',
    'chatbot',
]


# ============================================================
# ========== الـ Middleware (تم إصلاح الترتيب) ==========
# ============================================================
MIDDLEWARE = [
    'alumni_system.middleware.ForceLanguageMiddleware',  # ✅ الأول
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # يمكنك الاحتفاظ به أو حذفه
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# ========== إعدادات القوالب ==========
# ============================================================
ROOT_URLCONF = 'alumni_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dashboard.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'alumni_system.wsgi.application'


# ============================================================
# ========== قاعدة البيانات ==========
# ============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================================
# ========== التحقق من كلمة المرور ==========
# ============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# ========== إعدادات اللغة والوقت (تم الإصلاح) ==========
# ============================================================
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Aden'
USE_I18N = True
USE_L10N = True          # ✅ لتنسيق الأرقام والتواريخ بالعربية
USE_TZ = True

# ========== تعدد اللغات ==========
LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',  # ✅ تم التعديل: BASE_DI → BASE_DIR
]

# ✅ إجبار اللغة العربية عبر Cookie
LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365  # سنة كاملة

# ✅ تم حذف السطرين التاليين لأنهما يسببان خطأ AppRegistryNotReady:
# from django.utils.translation import activate
# activate('ar')


# ============================================================
# ========== الملفات الثابتة والوسائط ==========
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ============================================================
# ========== إعدادات DeepSeek API ==========
# ============================================================
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = 'https://api.deepseek.com/v1/chat/completions'


# ============================================================
# ========== Crispy Forms ==========
# ============================================================
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'


# ============================================================
# ========== تسجيل الدخول والخروج ==========
# ============================================================
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# ============================================================
# ========== النماذج الافتراضية ==========
# ============================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ============================================================
# ========== CORS ==========
# ============================================================
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True


# ============================================================
# ========== Django REST Framework + JWT ==========
# ============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}


# ============================================================
# ========== إعدادات البريد الإلكتروني ==========
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f'نظام متابعة الخريجين <{EMAIL_HOST_USER}>'


# ============================================================
# ========== ✅ إعدادات Celery (معلقة مؤقتاً) ==========
# ============================================================
# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_ACCEPT_CONTENT = ['json']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# ============================================================
# ========== ✅ إعدادات WebPush (معلقة مؤقتاً) ==========
# ============================================================
# WEBPUSH_SETTINGS = {
#     "VAPID_PRIVATE_KEY": "your_private_key",
#     "VAPID_PUBLIC_KEY": "your_public_key",
#     "VAPID_CLAIMS": {
#         "sub": "mailto:your-email@example.com"
#     }
# }