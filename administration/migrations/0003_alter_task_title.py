# Generated by Django 5.0.6 on 2024-08-08 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0002_alter_task_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(choices=[('create an internal passport', 'Створення внутрішнього паспорту'), ('create a foreign passport', 'Створення закордонного паспорту'), ('create a visa', 'Створення візи'), ('restore an internal passport due to loss', 'Відновлення внутрішнього паспорту через втрату'), ('restore a foreign passport due to loss', 'Відновлення закордонного паспорту через втрату'), ('restore an internal passport due to expiry', 'Відновлення внутрішнього паспорту через закінчення терміну дії'), ('restore a foreign passport due to expiry', 'Відновлення закордонного паспорту через закінчення терміну дії'), ('change user name', 'Зміна імені користувача'), ('change user surname', 'Зміна прізвища користувача'), ('change user patronymic', 'Зміна по батькові користувача'), ('change registation address', 'Оновлення адреси прописки')], max_length=255),
        ),
    ]
