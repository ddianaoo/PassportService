from django.test import TestCase
from passports.factories import AddressFactory, PassportFactory, ForeignPassportFactory
from passports.utils import COUNTRY_CHOICES


class TestFactories(TestCase):
    def test_address_factory(self):
        address = AddressFactory()
        self.assertIsNotNone(address.region)
        self.assertIsNotNone(address.settlement)
        self.assertIsNotNone(address.street)
        self.assertIsNotNone(address.apartments)
        self.assertIsNotNone(address.post_code)
        self.assertIn(address.country_code, [choice[0] for choice in COUNTRY_CHOICES])

    def test_passport_factory(self):
        passport = PassportFactory()
        self.assertIsNotNone(passport.number)
        self.assertIsNotNone(passport.authority)
        self.assertIsNotNone(passport.date_of_issue)
        self.assertIsNotNone(passport.date_of_expiry)
        self.assertIsNotNone(passport.photo)

    def test_foreign_passport_factory(self):
        passport = ForeignPassportFactory()
        self.assertIsNotNone(passport.number)
        self.assertIsNotNone(passport.authority)
        self.assertIsNotNone(passport.date_of_issue)
        self.assertIsNotNone(passport.date_of_expiry)
        self.assertIsNotNone(passport.photo)
