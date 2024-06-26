from authentication.models import CustomUser
from django.db import models


class Task(models.Model):
    STATUS_CHOICES = [
        (0, 'in progress'),
        (1, 'completed')
    ]
    TITLE_CHOICES = [
        ('Create ip', 'create new internal passport'),
        ('Create fp', 'create new foreign passport'),
        ('Create v', 'create new visa'),
        ('Restore ip - loss', 'restore an internal passport due to loss'),
        ('Restore fp - loss', 'restore an foreign passport due to loss'),
        ('Restore ip - expiry', 'restore an internal passport due to expiration'),
        ('Restore fp - expiry', 'restore an foreign passport due to expiration'),
        ('Change data', 'change passport data')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(choices=TITLE_CHOICES, max_length=50)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    user_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
