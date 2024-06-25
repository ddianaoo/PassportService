from authentication.models import CustomUser
from django.db import models


class Task(models.Model):
    STATUS_CHOICES = [
        (0, 'in progress'),
        (1, 'completed')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    user_data = models.JSONField()
