from random import randint

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from passports.models import Address, Passport, ForeignPassport
from passports.utils import COUNTRY_CHOICES
from validation.validate_birth_date import validate_birth_date
from validation.validate_email import validate_email
from validation.validate_record_number import validate_record_number


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser):
    GENDER_CHOICES = [
        ('F', 'Female'),
        ('M', 'Male'),
    ]
    COUNTRY_CHOICES = COUNTRY_CHOICES

    email          = models.EmailField(unique=True, validators=[validate_email,])
    name           = models.CharField(max_length=50)
    surname        = models.CharField(max_length=50)
    patronymic     = models.CharField(max_length=50)
    sex            = models.CharField(max_length=1, choices=GENDER_CHOICES) 
    date_of_birth  = models.DateField(validators=[validate_birth_date,])
    place_of_birth = models.CharField(max_length=255)
    nationality    = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    record_number  = models.CharField(max_length=14, unique=True, null=True, validators=[validate_record_number,]) 

    address          = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    passport         = models.OneToOneField(Passport, on_delete=models.SET_NULL, null=True, related_name='user')
    foreign_passport = models.OneToOneField(ForeignPassport, on_delete=models.SET_NULL, null=True, related_name='user')

    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    EMAIL_FIELD     = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'patronymic', 'sex', 'date_of_birth', 'place_of_birth', 'nationality']

    def __str__(self):
        return f"{self.name} {self.surname}"
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def save(self, *args, **kwargs):
        if not self.record_number:
            self.record_number = self.date_of_birth.strftime('%Y%m%d') + f'-{randint(1, 99999):05d}'
        super().save(*args, **kwargs)   
    