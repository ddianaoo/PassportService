from unittest.mock import ANY
from rest_framework import status
from rest_framework.test import APITestCase

from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from passports.factories import AddressFactory, PassportFactory


class UserAddressGetAPITests(APITestCase):
    """
    Test suite for retrieving user address information via the API.

    Tests various scenarios for the GET method of the address API endpoint:
    - Successful retrieval of the address
    - User without an address
    - Request without authentication
    - Request by an admin user who should be forbidden from accessing the address
    """
    def setUp(self):
        self.path = "/api/my-documents/address/"

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
            foreign_passport=None,
        )
        self.user_without_address = CustomUserFactory(
            email="test2@test.com",
            address=None,
            passport=None,
            foreign_passport=None,
        )
        self.admin = CustomUserFactory(
            email="admin@test.com",
            address=None,
            passport=None,
            foreign_passport=None,
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_get_address_successful(self):
        """
        Test that a user can successfully retrieve their address.

        Verifies that the API returns a 200 OK status and the correct address data for the authenticated user
        with the registration address.
        """
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {
                "id": ANY,
                "country_code": "UA",
                "region": "Kharkiv region",
                "settlement": "Kharkiv",
                "street": "Zoryana 4",
                "apartments": "88",
                "post_code": 61070
            },
            response.json()
        )

    def test_get_address_no_data(self):
        """
        Test that a user without a registration address receives a 200 status with a specific message.

        Verifies that the API returns a 200 OK status and the message indicating
        the user does not have a registration address.
        """
        self.client.force_authenticate(self.user_without_address)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": "You don`t have a registration address yet."},
            response.json()
        )

    def test_get_address_not_logged_in(self):
        """
        Test that unauthenticated users receive a 401 error.

        Verifies that the API returns a 401 Unauthorized status and the appropriate error message
        when no authentication credentials are provided.
        """
        self.client.force_authenticate(user=None)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_get_address_admin_logged_in_forbidden(self):
        """
        Test that an admin user receives a 403 error.

        Verifies that the API returns a 403 Forbidden status and the appropriate error message
        when an admin user attempts to access address data.
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )


class UserAddressPatchAPITests(APITestCase):
    """
    Test suite for updating user address information via the API.

    Tests various scenarios for the PATCH method of the address API endpoint:
    - Successful address update
    - Attempt to change address when a task is already stored
    - Attempt to change address when the user does not have a passport
    - Attempt to update address with no data provided
    - Attempt to update address with incorrect country code
    - Attempt to update address with incorrect post code
    - Unauthorized access and permission checks
    """
    def setUp(self):
        self.path = "/api/my-documents/address/"

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
            foreign_passport=None,
        )
        self.user_without_address = CustomUserFactory(
            email="test2@test.com",
            address=None,
            passport=None,
            foreign_passport=None,
        )
        self.admin = CustomUserFactory(
            email="admin@test.com",
            address=None,
            passport=None,
            foreign_passport=None,
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_change_address_successful(self):
        """
        Test that a user can successfully update their address.

        Verifies that the API returns a 200 OK status and the appropriate message
        when the address is updated successfully.
        Ensures that the notification task is triggered.
        """
        response = self.client.patch(
            path=self.path,
            data={
                "country_code": "UA",
                "region": "Kharkiv region",
                "settlement": "Kharkiv",
                "street": "Zoryana 4",
                "apartments": "11",
                "post_code": 61070
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": "Your request to update the registration address has been submitted."},
            response.json()
        )

    def test_change_address_task_already_stored(self):
        """
        Test that a user with an existing address update task cannot submit another request.

        Verifies that the API returns a 400 Bad Request status and the appropriate error message
        if a request to update the address is already pending.
        """
        TaskFactory(
            user=self.user,
            title='change registation address',
            status=0
        )
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You have already submitted a request to update your registration address."},
            response.json()
        )

    def test_change_address_no_pasport(self):
        """
        Test that a user without a passport cannot update their address.

        Verifies that the API returns a 400 Bad Request status and the appropriate error message
        when the user does not have a passport and attempts to update the address.
        """
        self.client.force_authenticate(self.user_without_address)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You do not have a passport, so updating the address is not possible."},
            response.json()
        )

    def test_change_address_no_data(self):
        """
        Test that a request to update the address with no data provided returns validation errors.

        Verifies that the API returns a 400 Bad Request status and the appropriate validation error messages
        when no data is provided in the request.
        """
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                'country_code': ['This field is required.'],
                'region': ['This field is required.'],
                'settlement': ['This field is required.'],
                'street': ['This field is required.'],
                'apartments': ['This field is required.'],
                'post_code': ['This field is required.']
            },
            response.json()
        )

    def test_change_address_incorrect_address_country_code(self):
        """
        Test that an incorrect country code results in a validation error.

        Verifies that the API returns a 400 Bad Request status and the appropriate error message
        when an invalid country code is provided.
        """
        invalid_country_code = "Ukraine"
        response = self.client.patch(
            path=self.path,
            data={
                "country_code": invalid_country_code,
                "region": "Kharkiv region",
                "settlement": "Kharkiv",
                "street": "Zoryana 4",
                "apartments": "11",
                "post_code": 61070,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'country_code': [f"\"{invalid_country_code}\" is not a valid choice."]},
            response.json()
        )

    def test_change_address_incorrect_address_post_code(self):
        """
        Test that an incorrect post code results in a validation error.

        Verifies that the API returns a 400 Bad Request status and the appropriate error message
        when an invalid post code is provided.
        """
        response = self.client.patch(
            path=self.path,
            data={
                "country_code": "UA",
                "region": "Kharkiv region",
                "settlement": "Kharkiv",
                "street": "Zoryana 4",
                "apartments": "11",
                "post_code": 100003,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'post_code': ["Post code must be positive and in the format xxxxx."]},
            response.json()
        )

    def test_change_address_not_logged_in(self):
        """
        Test that unauthenticated users receive a 401 error when attempting to update the address.

        Verifies that the API returns a 401 Unauthorized status and the appropriate error message
        when no authentication credentials are provided.
        """
        self.client.force_authenticate(user=None)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_change_address_admin_logged_in_forbidden(self):
        """
        Test that an admin user receives a 403 error when attempting to update a user's address.

        Verifies that the API returns a 403 Forbidden status and the appropriate error message
        when an admin user tries to update a user's address, which should be restricted to regular users.
        """
        self.client.force_authenticate(self.admin)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )
