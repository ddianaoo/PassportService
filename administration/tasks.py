from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_notification(subject, message, user_emails):
    send_mail(
        subject=subject,
        message=message,
        from_email='passport.service.test@gmail.com',
        recipient_list=user_emails,
        fail_silently=False,
    )
