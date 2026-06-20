from celery import shared_task
from dashboard.notifications import send_email_notification, send_sms_notification

@shared_task
def send_email_task(recipient_email, subject, message):
    send_email_notification(recipient_email, subject, message)

@shared_task
def send_sms_task(phone_number, message):
    send_sms_notification(phone_number, message)