# Generated by Django 5.0.6 on 2024-07-09 14:08

import validation.validate_authority
import validation.validate_expiry_date
import validation.validate_issue_date
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passports', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foreignpassport',
            name='authority',
            field=models.IntegerField(validators=[validation.validate_authority.validate_authority]),
        ),
        migrations.AlterField(
            model_name='foreignpassport',
            name='date_of_expiry',
            field=models.DateField(validators=[validation.validate_expiry_date.validate_expiry_date]),
        ),
        migrations.AlterField(
            model_name='foreignpassport',
            name='date_of_issue',
            field=models.DateField(validators=[validation.validate_issue_date.validate_issue_date]),
        ),
        migrations.AlterField(
            model_name='foreignpassport',
            name='photo',
            field=models.ImageField(upload_to='photos/passports/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='passport',
            name='authority',
            field=models.IntegerField(validators=[validation.validate_authority.validate_authority]),
        ),
        migrations.AlterField(
            model_name='passport',
            name='date_of_expiry',
            field=models.DateField(validators=[validation.validate_expiry_date.validate_expiry_date]),
        ),
        migrations.AlterField(
            model_name='passport',
            name='date_of_issue',
            field=models.DateField(validators=[validation.validate_issue_date.validate_issue_date]),
        ),
        migrations.AlterField(
            model_name='passport',
            name='photo',
            field=models.ImageField(upload_to='photos/passports/%Y/%m/%d/'),
        ),
    ]
