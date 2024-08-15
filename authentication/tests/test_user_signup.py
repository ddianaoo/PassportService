# python3 manage.py test authentication.tests
from authentication.factories import CustomUserFactory
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY


class UserRegistrationAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUserFactory(email="test@test.com")
        self.path = "/api/auth/users/"

    def test_register_user_successful(self):
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@test.com",
                "password": "rewq4321",
                "re_password": "rewq4321",	
                "sex": "F",
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
	            "sex": "F",
	            "date_of_birth": "1978-11-18",
	            "place_of_birth": "Kharkiv",
	            "nationality": "UA",
                "email": "jane@test.com",
	            "id": ANY
            },
            response.json(),
        )

    def test_register_user_email_incorrect(self):
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@testcom",
                "password": "rewq4321",
                "re_password": "rewq4321",	
                "sex": "F",
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"email": ["The email address is not valid.", "Enter a valid email address."]},
            response.json(),
        )

    def test_register_user_email_exists(self):
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "test@test.com",
                "password": "rewq4321",
                "re_password": "rewq4321",	
                "sex": "F",
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"email": ["custom user with this email already exists."]},
            response.json(),
        )

    def test_register_user_password_incorrect_short(self):
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@test.com",
                "password": "rewq",
                "re_password": "rewq",	
                "sex": "F",
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                "password": [
                    "This password is too short. It must contain at least 8 characters."
                ]
            },
            response.json(),
        )

    def test_register_user_password_incorrect_common(self):
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@test.com",
                "password": "12345678",
                "re_password": "12345678",	
                "sex": "F",
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"password": [
		        "This password is too common.",
		        "This password is entirely numeric."
            ]},
            response.json(),
        )

    def test_register_user_password_incorrect_dont_match(self):
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@test.com",
                "password": "rewq4321",
                "re_password": "rewq4322",	
                "sex": "F",
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"non_field_errors": [ "The two password fields didn't match."]},
            response.json(),
        )

    def test_register_user_sex_incorrect(self):
        sex = "Female"
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@test.com",
                "password": "rewq4321",
                "re_password": "rewq4321",	
                "sex": sex,
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"sex": [f"\"{sex}\" is not a valid choice."]},
            response.json(),
        )

    def test_register_user_nationality_incorrect(self):
        nationality = "UAa"
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@test.com",
                "password": "rewq4321",
                "re_password": "rewq4321",	
                "sex": "F",
                "date_of_birth": "1978-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": nationality
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"nationality": [f"\"{nationality}\" is not a valid choice."]},
            response.json(),
        )

    def test_register_user_date_of_birth_incorrect(self):
        response = self.client.post(
            path=self.path,
            data = {
                "name": "Jane",
                "surname": "Smith",
                "patronymic": "Dmitrivna",
                "email": "jane@test.com",
                "password": "rewq4321",
                "re_password": "rewq4321",	
                "sex": "F",
                "date_of_birth": "2011-11-18",
                "place_of_birth": "Kharkiv",
                "nationality": "UA"
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"date_of_birth": ["You must be at least 14 years old."]},
            response.json(),
        )
