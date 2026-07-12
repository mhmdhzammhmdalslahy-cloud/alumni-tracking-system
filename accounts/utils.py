from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_verification_email(user, code):
    """إرسال رمز التأكيد عبر البريد الإلكتروني"""
    subject = '🔐 رمز تأكيد الحساب - جامعة إقليم سبأ'
    
    html_message = render_to_string('accounts/email_verification.html', {
        'user': user,
        'code': code,
        'university_name': 'جامعة إقليم سبأ'
    })
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )