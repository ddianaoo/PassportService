from authentication.factories import CustomUserFactory
from passports.utils import COUNTRY_CHOICES_DICT
from passports.factories import AddressFactory, PassportFactory, ForeignPassportFactory
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY


class GetDocumentsAPITests(APITestCase):
    def setUp(self):
        self.path = "/api/my-documents/"

        address = AddressFactory(
            country_code="UA",
            region="Kharkiv region",
            settlement="Kharkiv",
            street="Zoryana 4",
            apartments="88",
            post_code=61070
        )
        self.user = CustomUserFactory(
            email="test@test.com",
            address=address,
            passport=PassportFactory(photo=''),
            foreign_passport=ForeignPassportFactory(photo=''),
        )
        self.admin = CustomUserFactory(
            email="admin@test.com",
            address=None,
            passport=None,
            foreign_passport=None,
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.user_nationality = COUNTRY_CHOICES_DICT[self.user.nationality]
        self.internal_passport_data = {
            "number": ANY,
            "authority": self.user.passport.authority,
            "date_of_issue": str(self.user.passport.date_of_issue),
            "date_of_expiry": str(self.user.passport.date_of_expiry),
            "photo": ANY,  
            "name": self.user.name,  
            "surname": self.user.surname,  
            "patronymic": self.user.patronymic,   
            "sex": self.user.sex,
            "date_of_birth": str(self.user.date_of_birth),
            "record_number": self.user.record_number,
            "place_of_birth": self.user.place_of_birth,
            "nationality": self.user_nationality,
            "registration_address": {
                "id": ANY,
                "country_code": self.user.address.country_code,
                "region": self.user.address.region,
                "settlement": self.user.address.settlement,
                "street": self.user.address.street,
                "apartments": self.user.address.apartments,
                "post_code": self.user.address.post_code
            }
        }    
        self.foreign_passport_data = {
            "number": ANY,
            "authority": self.user.foreign_passport.authority,
            "date_of_issue": str(self.user.foreign_passport.date_of_issue),
            "date_of_expiry": str(self.user.foreign_passport.date_of_expiry),
            "photo": ANY,  
            "name": self.user.name,  
            "surname": self.user.surname,  
            "patronymic": self.user.patronymic,   
            "sex": self.user.sex,
            "date_of_birth": str(self.user.date_of_birth),
            "record_number": self.user.record_number,
            "place_of_birth": self.user.place_of_birth,
            "country_code": self.user.nationality,
            "nationality": self.user_nationality,  
        }

    # GET METHOD
    def test_get_documents_full_data(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            "internal_passport": self.internal_passport_data,
            "foreign_passport": self.foreign_passport_data,
        },
            response.json()
        )

    def test_get_documents_no_foreign_passport(self):
        self.user.foreign_passport = None
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            "internal_passport": self.internal_passport_data,
            "foreign_passport": None,
        },
            response.json()
        )

    def test_get_documents_no_both_passports(self):
        self.user.passport = None
        self.user.foreign_passport = None
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            "internal_passport": None,
            "foreign_passport": None
        },
            response.json()
        )

    def test_get_documents_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_get_documents_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )
