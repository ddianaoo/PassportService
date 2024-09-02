import os
from django.db.models.signals import post_save
from django.dispatch import receiver

from authentication.models import CustomUser
from .models import Task
from .tasks import send_notification
from .utils import DICT_TITLES_SLUGS

HOST = os.environ.get('LOCAL_URL')


@receiver(post_save, sender=Task)
def notify_admins_on_new_task(sender, instance, created, **kwargs):
    if created:
        admins = CustomUser.objects.filter(is_staff=True)
        email_addresses = [admin.email for admin in admins]

        title = DICT_TITLES_SLUGS[instance.title]
        link_url = f"{HOST}/staff/{title}/{instance.id}"

        if email_addresses:
            send_notification.delay(
                subject='New Request Created',
                message=f'A new request "{instance.title}" has been created by {instance.user}.\nYou can view it here: {link_url}',
                user_emails=email_addresses
            )

@receiver(post_save, sender=Task)
def notify_user_on_task_resolved(sender, instance, **kwargs):
    if instance.status == 1:
        link = f"{HOST}/my-documents/"
        send_notification.delay(
            subject=f'Your Request "{instance.title}" Has Been Resolved',
            message=f'Hello {instance.user.name},\nYour request "{instance.title}" has been resolved.\nFollow this link to view your documents: {link}',
            user_emails=[instance.user.email]
        )

@receiver(post_save, sender=Task)
def notify_user_on_task_resolved(sender, instance, **kwargs):
    if instance.status == 2:
        send_notification.delay(
            subject=f'Your Request "{instance.title}" Has Been Rejected',
            message=f'Hello {instance.user.name},\nYour request "{instance.title}" has been rejected.',
            user_emails=[instance.user.email]
        )
