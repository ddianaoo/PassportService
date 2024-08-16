from authentication.models import CustomUser
from django.db import models


class Task(models.Model):
    STATUS_CHOICES = [
        (0, 'in progress'),
        (1, 'completed')
    ]
    TITLE_CHOICES = [
        ('create an internal passport', 'Створення внутрішнього паспорту'),
        ('create a foreign passport', 'Створення закордонного паспорту'),
        ('create a visa', 'Створення візи'),
        ('restore an internal passport due to loss', 'Відновлення внутрішнього паспорту через втрату'),
        ('restore a foreign passport due to loss', 'Відновлення закордонного паспорту через втрату'),
        ('restore an internal passport due to expiry', 'Відновлення внутрішнього паспорту через закінчення терміну дії'),
        ('restore a foreign passport due to expiry', 'Відновлення закордонного паспорту через закінчення терміну дії'),
        ('change user name', 'Зміна імені користувача'),
        ('change user surname', 'Зміна прізвища користувача'),
        ('change user patronymic', 'Зміна по батькові користувача'),
        ('change registation address', 'Оновлення адреси прописки')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(choices=TITLE_CHOICES, max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    user_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"<Task {self.id}: `{self.title}`>"
