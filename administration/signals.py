
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from authentication.models import CustomUser
from .models import Task


TASK_ENDPOINTS = (
            'create-passport', 
            'create-foreign-passport', 
            'create-visa', 
            'restore-passport', 
            'restore-fpassport',
            'restore-passport', 
            'restore-fpassport', 
            'change-name', 
            'change-surname', 
            'change-patronymic', 
            'change-address', 
    )

@receiver(post_save, sender=Task)
def notify_admins_on_new_task(sender, instance, created, **kwargs):
    if created:
        admins = CustomUser.objects.filter(is_staff=True, is_superuser=True)
        email_addresses = [admin.email for admin in admins]

        paths_dict = dict(zip([i[0] for i in Task.TITLE_CHOICES], TASK_ENDPOINTS))
        title = paths_dict[instance.title]
        link_url = f"http://127.0.0.1:8000/staff/{title}/{instance.id}"

        if email_addresses:
            send_mail(
                subject='New Request Created',
                message=f'A new request "{instance.title}" has been created by {instance.user}.\nYou can view the it here: {link_url}',
                from_email='passport.service.test@gmail.com',
                recipient_list=email_addresses,
                fail_silently=False,
            )

@receiver(post_save, sender=Task)
def notify_user_on_task_resolved(sender, instance, **kwargs):
    if instance.status == 1:
        user_email = instance.user.email
        link = "http://127.0.0.1:8000/my-documents/"
        send_mail(
            subject='Your Request Has Been Resolved',
            message=f'Hello {instance.user.name},\nYour request "{instance.title}" has been resolved.\nFollow this link to view your documents: {link}',
            from_email='passport.service.test@gmail.com',
            recipient_list=[user_email],
            fail_silently=False,
        )
