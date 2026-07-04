import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth.models import User
from dashboard.models import AdminProfile

for user in User.objects.filter(is_superuser=True):
    profile, created = AdminProfile.objects.get_or_create(
        user=user,
        defaults={'admin_level': 'super_admin', 'is_active': True}
    )
    if created:
        print(f"✅ تم إنشاء AdminProfile للمشرف: {user.username}")
    else:
        print(f"ℹ️ AdminProfile موجود مسبقاً للمشرف: {user.username}")



