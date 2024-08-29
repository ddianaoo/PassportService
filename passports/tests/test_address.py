from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY, patch

from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from passports.factories import AddressFactory, PassportFactory


class UserAddressAPITests(APITestCase):
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
        self.valid_address_data = {
	        "country_code": "UA",
	        "region": "Kharkiv region",
	        "settlement": "Kharkiv",
	        "street": "Zoryana 4",
	        "apartments": "11",
	        "post_code": 61070
        }

    # GET METHOD
    def test_get_address_successful(self):
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
        self.client.force_authenticate(self.user_without_address)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            {"detail": "Registration address not found."},
            response.json()
        )

    def test_get_address_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_get_address_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )

    # PATCH METHOD
    @patch('administration.tasks.send_notification.delay')
    def test_change_address_successful(self, mock_send_notification):
        response = self.client.patch(
            path=self.path,
            data={**self.valid_address_data},
            format='json'                       
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": "Your request to update the registration address has been submitted."},
            response.json()
        )
        mock_send_notification.assert_called_once()

    def test_change_address_task_already_stored(self):
        task = TaskFactory(
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
        self.client.force_authenticate(self.user_without_address)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You do not have a passport, so updating the address is not possible."},
            response.json()
        )

    def test_change_address_no_data(self):
        response = self.client.patch(path=self.path,data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
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
        self.client.force_authenticate(user=None)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_change_address_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )
