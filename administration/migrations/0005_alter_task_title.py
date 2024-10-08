# Generated by Django 5.0.6 on 2024-09-02 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0004_alter_task_status_alter_task_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(choices=[('create an internal passport', 'Створення внутрішнього паспорту'), ('create a foreign passport', 'Створення закордонного паспорту'), ('create a visa', 'Створення візи'), ('extend a visa', 'Подовження візи'), ('restore a visa due to loss', 'Відновлення візи'), ('restore an internal passport due to loss', 'Відновлення внутрішнього паспорту через втрату'), ('restore a foreign passport due to loss', 'Відновлення закордонного паспорту через втрату'), ('restore an internal passport due to expiry', 'Відновлення внутрішнього паспорту через закінчення терміну дії'), ('restore a foreign passport due to expiry', 'Відновлення закордонного паспорту через закінчення терміну дії'), ('change user name', 'Зміна імені користувача'), ('change user surname', 'Зміна прізвища користувача'), ('change user patronymic', 'Зміна по батькові користувача'), ('change registation address', 'Оновлення адреси прописки')], max_length=255),
        ),
    ]
