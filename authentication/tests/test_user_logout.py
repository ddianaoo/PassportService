from authentication.factories import CustomUserFactory
from rest_framework import status
from rest_framework.test import APITestCase


class UserLogoutAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUserFactory(email="test@test.com")
        self.path_login = "/api/auth/token/login/"
        self.path_logout = "/api/auth/token/logout/"

    def test_logout_successful(self):
        self.user.set_password("Test1234")
        self.user.save()

        self.test_user_token = self.client.post(
            path=self.path_login,
            data={
                "email": "test@test.com",
                "password": "Test1234",
            },
        ).data["auth_token"]
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.test_user_token}"
        )
        response = self.client.post(path=self.path_logout)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_not_logged_in(self):
        response = self.client.post(path=self.path_logout)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json(),
        )
