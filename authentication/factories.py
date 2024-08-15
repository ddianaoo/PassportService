import factory.django
import factory.fuzzy
from .models import CustomUser
import datetime


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
        django_get_or_create = ("email",)

    email          = factory.Sequence(lambda n: f"test{n + 1}@test.com")
    name           = factory.Sequence(lambda n: f"Test name{n + 1}")
    surname        = factory.Sequence(lambda n: f"Test surname{n + 1}")
    password       = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    patronymic     = factory.Sequence(lambda n: f"Test patronymic{n + 1}")
    sex            = factory.fuzzy.FuzzyChoice(CustomUser.GENDER_CHOICES, getter=lambda c: c[0])
    date_of_birth  = factory.fuzzy.FuzzyDate(datetime.date(1950, 1, 1), datetime.date(2010, 1, 1))
    place_of_birth = factory.Sequence(lambda n: f"Test place{n + 1}")
    nationality    = factory.fuzzy.FuzzyChoice(CustomUser.COUNTRY_CHOICES, getter=lambda c: c[0])
    is_active      = True
