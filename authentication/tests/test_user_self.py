from authentication.factories import CustomUserFactory
import datetime
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY


class UserSelfAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUserFactory(
            email="test@test.com",
            name="Test",
            surname="Test",
            patronymic="Testovich",
            date_of_birth=datetime.date(2000, 1, 1),
            record_number="20000101-33509",
            nationality="UA",
            sex="M",
            place_of_birth="Kharkiv",
        )
        self.path = "/api/auth/users/me/"

    def test_user_retreive_data_successful(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
        {
	        "id": ANY,
	        "name": "Test",
	        "surname": "Test",
	        "patronymic": "Testovich",
	        "email": "test@test.com",
	        "sex": "M",
	        "date_of_birth": "2000-01-01",
	        "place_of_birth": "Kharkiv",
	        "nationality": "UA",
	        "record_number": "20000101-33509",
	        "address": None,
	        "passport": None,
	        "foreign_passport": None
        },
            response.json(),
        )

    def test_user_retreive_data_not_logged_in(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json(),
        )

    def test_user_update_all_fields_forbidden(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(
            path=self.path,
            data={
	            "id": ANY,
	            "name": "Ivan",
	            "surname": "Ivanenko",
	            "patronymic": "Ivanov",
	            "email": "test@test.com",
	            "sex": "M",
	            "date_of_birth": "2000-01-01",
	            "place_of_birth": "Kharkiv",
	            "nationality": "UA",
	            "record_number": "20000101-11111",
	            "address": ANY,
	            "passport": ANY,
	            "foreign_passport": ANY
        },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json(),
        )

    def test_user_update_one_field__forbidden(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            path=self.path,
            data={ "surname": "Petrenko"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json(),
        )

    def test_user_delete_forbidden(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(
            path=self.path,
            data={"password": "Test1234"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json(),
        )
