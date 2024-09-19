import random
from django.db import models

from validation.validate_authority import validate_authority
from validation.validate_expiry_date import validate_expiry_date
from validation.validate_issue_date import validate_issue_date
from validation.validate_number import validate_number
from validation.validate_post_code import validate_post_code
from .utils import COUNTRY_CHOICES


class Address(models.Model):
    COUNTRY_CHOICES = COUNTRY_CHOICES

    country_code = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    region       = models.CharField(max_length=100)
    settlement   = models.CharField(max_length=100)
    street       = models.CharField(max_length=100)
    apartments   = models.CharField(max_length=10)
    post_code    = models.IntegerField(validators=[validate_post_code,])

    def __str__(self) -> str:
        return f"Address: {self.country_code}, {self.region}, {self.settlement}, {self.street}, {self.apartments}"


class AbstractPassport(models.Model):
    number         = models.IntegerField(primary_key=True, validators=[validate_number,])
    authority      = models.IntegerField(validators=[validate_authority,])
    date_of_issue  = models.DateField(validators=[validate_issue_date])
    date_of_expiry = models.DateField(validators=[validate_expiry_date])
    photo          = models.ImageField(upload_to='photos/passports/%Y/%m/%d/')

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
        return super().__str__() + "(Internal Passport)"


class ForeignPassport(AbstractPassport):
    def __str__(self):
        return super().__str__() + "(Foreign Passport)"


class Visa(models.Model):
    COUNTRY_CHOICES = COUNTRY_CHOICES

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
    place_of_issue   = models.CharField(max_length=50)
    date_of_issue    = models.DateField(validators=[validate_issue_date])
    date_of_expiry   = models.DateField(validators=[validate_expiry_date])
    photo            = models.ImageField(upload_to='photos/visas/%Y/%m/%d/')
    type             = models.CharField(max_length=50, choices=TYPE_CHOICES)
    country          = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    entry_amount     = models.CharField(max_length=4, choices=ENTRY_CHOICES)
    is_active        = models.BooleanField(default=True)

    def __str__(self):
        return f"Visa to {self.country}. Expiration date: {self.date_of_expiry})"

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = random.randint(10000000, 99999999)
        super().save(*args, **kwargs)
