from django import template
from dashboard.models import SystemSetting

register = template.Library()

@register.simple_tag
def get_setting(key, default=''):
    try:
        setting = SystemSetting.objects.get(key=key)
        return setting.value
    except SystemSetting.DoesNotExist:
        return default