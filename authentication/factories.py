import datetime
from random import randint

import factory.django
import factory.fuzzy

from .models import CustomUser
from passports.factories import AddressFactory, PassportFactory, ForeignPassportFactory 


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ("email",)

    email          = factory.Sequence(lambda n: f"test{n + 1}@test.com")
    name           = factory.Sequence(lambda n: f"Testname{n + 1}")
    surname        = factory.Sequence(lambda n: f"Testsurname{n + 1}")
    password       = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    patronymic     = factory.Sequence(lambda n: f"Testpatronymic{n + 1}")
    sex            = factory.fuzzy.FuzzyChoice(CustomUser.GENDER_CHOICES, getter=lambda c: c[0])
    date_of_birth  = factory.fuzzy.FuzzyDate(datetime.date(1950, 1, 1), datetime.date(2010, 1, 1))
    place_of_birth = factory.Sequence(lambda n: f"Testplace{n + 1}")
    nationality    = factory.fuzzy.FuzzyChoice(CustomUser.COUNTRY_CHOICES, getter=lambda c: c[0])

    address          = factory.SubFactory(AddressFactory)
    passport         = factory.SubFactory(PassportFactory)
    foreign_passport = factory.SubFactory(ForeignPassportFactory)

    record_number = factory.LazyAttribute(lambda o: o.date_of_birth.strftime('%Y%m%d') + f'-{randint(1, 99999):05d}')
    is_active      = True
    is_staff       = False 
