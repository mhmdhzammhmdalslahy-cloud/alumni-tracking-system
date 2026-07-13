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
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # ✅ مطلوب لـ Allauth
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'whitenoise.runserver_nostatic',
    
    # ✅ Allauth (للحسابات فقط - تم تعطيل socialaccount)
    'allauth',
    'allauth.account',
    # 'allauth.socialaccount',  # ❌ معطل مؤقتاً
    # 'allauth.socialaccount.providers.google',  # ❌ معطل مؤقتاً
    
    # ✅ المصادقة الثنائية (2FA)
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'two_factor',
    
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
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ✅ OTPMiddleware بعد AuthenticationMiddleware
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # ✅ Allauth middleware
    'allauth.account.middleware.AccountMiddleware',
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
            # ✅ إضافة فلتر التحقق المخصص
            'libraries': {
                'validation_filters': 'templatetags.validation_filters',
            }
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
# ========== إعدادات اللغة والوقت ==========
# ============================================================
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Aden'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

LANGUAGE_COOKIE_NAME = 'django_language'
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365


# ============================================================
# ========== الملفات الثابتة والوسائط ==========
# ============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000

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
LOGIN_REDIRECT_URL = '/dashboard/'
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
# ========== ✅ إعدادات Allauth (Google Login, Reset Password) ==========
# ============================================================
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SITE_ID = 1

# ✅ إعدادات Allauth الجديدة (تجنب التحذيرات)
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_RATE_LIMITS = {
    'login_failed': '5/300s',  # 5 محاولات كل 5 دقائق
}

# ❌ تم تعطيل Google OAuth مؤقتاً
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'APP': {
#             'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
#             'secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
#             'key': ''
#         },
#         'SCOPE': ['profile', 'email'],
#         'AUTH_PARAMS': {'access_type': 'online'},
#         'METHOD': 'oauth2'
#     }
# }

# SOCIALACCOUNT_LOGIN_ON_GET = True  # ❌ معطل


# ============================================================
# ========== ✅ إعدادات المصادقة الثنائية (2FA) ==========
# ============================================================
TWO_FACTOR_PATCH_ADMIN = True


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


# ============================================================
# ========== ✅ إعدادات النطاق (Domain) لـ Render ==========
# ============================================================
try:
    from django.contrib.sites.models import Site
    
    # حذف جميع المواقع الحالية
    Site.objects.all().delete()
    
    # إنشاء الموقع الصحيح
    site = Site.objects.create(
        id=1,
        domain='alumni-tracking-system-bga6.onrender.com',
        name='نظام متابعة الخريجين'
    )
    print(f"✅ تم تحديث النطاق: {site.domain}")
except Exception as e:
    print(f"⚠️ لم يتم تحديث النطاق: {e}")