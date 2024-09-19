import os
import random

import factory
import factory.fuzzy
from django.utils import timezone
from django.conf import settings

from authentication.models import CustomUser
from .models import Address, Passport, ForeignPassport, Visa
from .utils import COUNTRY_CHOICES


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    country_code = factory.fuzzy.FuzzyChoice(CustomUser.COUNTRY_CHOICES, getter=lambda c: c[0])
    region       = factory.Sequence(lambda n: f"Test region{n + 1}")
    settlement   = factory.Sequence(lambda n: f"Test settlement{n + 1}")
    street       = factory.Sequence(lambda n: f"Test street{n + 1}")
    apartments   = factory.Sequence(lambda n: f"Test apartments{n + 1}")
    post_code    = factory.LazyAttribute(lambda _: random.randint(1111, 9999))


class AbstractPassportFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    number         = factory.LazyAttribute(lambda _: random.randint(10000000, 99999999))
    authority      = factory.LazyAttribute(lambda _: random.randint(1111, 9999))
    date_of_issue  = factory.LazyAttribute(lambda _: timezone.now().date())
    date_of_expiry = factory.LazyAttribute(lambda o: o.date_of_issue + timezone.timedelta(days=365 * 10 + 2))


class PassportFactory(AbstractPassportFactory):
    class Meta:
        model = Passport

    photo = factory.django.ImageField(from_path=os.path.join(settings.MEDIA_ROOT, 'tests/create_ip.png'),
                                      filename="TEST-internal-passport.jpeg")


class ForeignPassportFactory(AbstractPassportFactory):
    class Meta:
        model = ForeignPassport

    photo = factory.django.ImageField(from_path=os.path.join(settings.MEDIA_ROOT, 'tests/create_fp.jpg'), filename="TEST-foreign-passport.jpeg")


class VisaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Visa

    number           = factory.LazyAttribute(lambda _: random.randint(10000000, 99999999))
    foreign_passport = factory.SubFactory(ForeignPassportFactory)
    place_of_issue   = factory.Sequence(lambda n: f"Test place{n + 1}")
    date_of_issue    = factory.LazyAttribute(lambda _: timezone.now().date())
    date_of_expiry   = factory.LazyAttribute(lambda o: o.date_of_issue + timezone.timedelta(days=365 * 10 + 2))
    photo            = factory.django.ImageField(from_path=os.path.join(settings.MEDIA_ROOT, 'tests/create_visa.jpg'), filename="TEST-visa.jpeg")
    type             = factory.fuzzy.FuzzyChoice(Visa.TYPE_CHOICES, getter=lambda c: c[0])
    country          = factory.fuzzy.FuzzyChoice(COUNTRY_CHOICES, getter=lambda c: c[0])
    entry_amount     = factory.fuzzy.FuzzyChoice(Visa.ENTRY_CHOICES, getter=lambda c: c[0])
