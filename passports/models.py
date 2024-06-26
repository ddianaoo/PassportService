from django.db import models
from validation.validate_authority import validate_authority
from validation.validate_expiry_date import validate_expiry_date
from validation.validate_issue_date import validate_issue_date
from validation.validate_number import validate_number
from validation.validate_post_code import validate_post_code
from validation.validate_record_number import validate_record_number
import random
from .utils import COUNTRY_CHOICES, REGION_CHOICES


class Address(models.Model):
    COUNTRY_CHOICES = COUNTRY_CHOICES
    REGION_CHOICES = REGION_CHOICES

    country_code = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    region       = models.CharField(max_length=25, choices=REGION_CHOICES)
    settlement   = models.CharField(max_length=100)
    district     = models.CharField(max_length=100)
    street       = models.CharField(max_length=100)
    apartments   = models.CharField(max_length=10)
    post_code    = models.IntegerField(validators=[validate_post_code,])


class AbstractPassport(models.Model):
    number         = models.IntegerField(primary_key=True, validators=[validate_number,])
    record_number  = models.CharField(max_length=14, unique=True, blank=True, validators=[validate_record_number,]) 
    authority      = models.IntegerField(blank=True, validators=[validate_authority,])
    date_of_issue  = models.DateField(blank=True, validators=[validate_issue_date])
    date_of_expiry = models.DateField(blank=True, validators=[validate_expiry_date])
    photo          = models.ImageField(upload_to='photos/passports/%Y/%m/%d/', blank=True)
    
    class Meta:
        abstract = True

    def __str__(self):
        return f"Document number: {self.number}"
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = random.randint(10000000, 99999999)
        super().save(*args, **kwargs)


class Passport(AbstractPassport):
    def __str__(self):
        return super().__str__()+"(Internal Passport)"
    

class ForeignPassport(AbstractPassport):
    def __str__(self):
        return super().__str__()+"(Foreign Passport)"


class Visa(models.Model):
    COUNTRY_CHOICES = COUNTRY_CHOICES    
    REGION_CHOICES = REGION_CHOICES
    ENTRY_CHOICES = [
        ('1', 'Single Entry'),
        ('2', 'Double Entry'),
        ('MULT', 'Multiple Entry')
    ]

    TYPE_CHOICES = [
        ('Employment', 'Employment Type'),
        ('Business', 'Business Type'),
        ('Tourist', 'Tourist Type'),
        ('Student', 'Student Type'),
        ('Transit', 'Transit Type'),
    ]

    number           = models.IntegerField(primary_key=True, validators=[validate_number,])

    foreign_passport = models.ForeignKey(ForeignPassport, related_name='visas', on_delete=models.CASCADE)
    place_of_issue   = models.CharField(max_length=25, choices=REGION_CHOICES)
    date_of_issue  = models.DateField(blank=True, validators=[validate_issue_date])
    date_of_expiry = models.DateField(blank=True, validators=[validate_expiry_date])
    photo            = models.ImageField(upload_to='photos/visas/%Y/%m/%d/', blank=True)
    type             = models.CharField(max_length=50, choices=TYPE_CHOICES, default='Tourist') 
    country          = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    entry_amount     = models.CharField(max_length=4, choices=ENTRY_CHOICES, default='1')
    
    def __str__(self):
        return f"Visa to {self.country}.Expiration date: {self.expiry_date})"
    

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = random.randint(10000000, 99999999)
        super().save(*args, **kwargs)
    