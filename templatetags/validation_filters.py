from django import template
import re

register = template.Library()

@register.filter
def sanitize(value):
    """تنظيف الإدخالات تلقائياً"""
    if not value:
        return value
    
    value = str(value)
    
    # إذا كان يحتوي على أرقام فقط → احتفظ بالأرقام فقط
    if re.match(r'^[\d]+$', value):
        return re.sub(r'[^0-9]', '', value)
    
    # إذا كان يحتوي على حروف فقط → احتفظ بالحروف فقط
    elif re.match(r'^[\u0621-\u064A\u0660-\u0669a-zA-Z\s]+$', value):
        return re.sub(r'[^a-zA-Z\u0621-\u064A\u0660-\u0669\s]', '', value)
    
    # البريد الإلكتروني
    elif '@' in value and '.' in value:
        return value
    
    # الوضع الطبيعي
    return value

@register.filter
def validate_type(value, field_type):
    """التحقق من نوع الحقل"""
    if not value:
        return True
    
    value = str(value)
    
    if field_type == 'letters':
        return bool(re.match(r'^[\u0621-\u064A\u0660-\u0669a-zA-Z\s]+$', value))
    elif field_type == 'numbers':
        return bool(re.match(r'^\d+$', value))
    elif field_type == 'both':
        return bool(re.match(r'^[\u0621-\u064A\u0660-\u0669a-zA-Z0-9\s]+$', value))
    elif field_type == 'phone':
        return bool(re.match(r'^(0|7|9)\d{8,9}$', value))
    else:
        return True