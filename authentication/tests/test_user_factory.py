from django.test import TestCase
from authentication.factories import CustomUserFactory
from authentication.models import CustomUser


class TestFactories(TestCase):
    def test_user_factory(self):
        user = CustomUserFactory()
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.name)
        self.assertIsNotNone(user.surname)
        self.assertIsNotNone(user.patronymic)
        self.assertIn(user.sex, [choice[0] for choice in CustomUser.GENDER_CHOICES])
        self.assertIsNotNone(user.date_of_birth)
        self.assertIsNotNone(user.place_of_birth)
        self.assertIn(user.nationality, [choice[0] for choice in CustomUser.COUNTRY_CHOICES])

        self.assertIsNotNone(user.address)
        self.assertIsNotNone(user.passport)
        self.assertIsNotNone(user.foreign_passport)

        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertIsNotNone(user.record_number)
