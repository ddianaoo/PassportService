from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
from passports.utils import COUNTRY_CHOICES_DICT
from passports.factories import AddressFactory, PassportFactory, ForeignPassportFactory
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY


class UserDataAPITests(APITestCase):
    def setUp(self):
        self.path = "/api/my-documents/user-data/"

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
        self.user_without_passport = CustomUserFactory(
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

        self.user_data = {
	        "id": ANY,
            "name": self.user.name,  
            "surname": self.user.surname,  
            "patronymic": self.user.patronymic,   
	        "email": self.user.email,
            "sex": self.user.sex,
            "date_of_birth": str(self.user.date_of_birth),
            "record_number": self.user.record_number,
            "place_of_birth": self.user.place_of_birth,
            "nationality": self.user.nationality
        }

        self.image_path = os.path.join(settings.MEDIA_ROOT, 'tests/change_userdata.jpg')

    # GET METHOD
    def test_get_user_data_full_data(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            **self.user_data,
            "address": {
                "id": ANY,
                "country_code": self.user.address.country_code,
                "region": self.user.address.region,
                "settlement": self.user.address.settlement,
                "street": self.user.address.street,
                "apartments": self.user.address.apartments,
                "post_code": self.user.address.post_code
            },
	        "passport": ANY,
	        "foreign_passport": ANY
            },
            response.json()
        )

    def test_get_user_data_no_foreign_passport(self):
        self.user.foreign_passport = None
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            **self.user_data,
            "address": {
                "id": ANY,
                "country_code": self.user.address.country_code,
                "region": self.user.address.region,
                "settlement": self.user.address.settlement,
                "street": self.user.address.street,
                "apartments": self.user.address.apartments,
                "post_code": self.user.address.post_code
            },
	        "passport": ANY,
	        "foreign_passport": None
            },
            response.json()
        )

    def test_get_user_data_no_both_passports(self):
        self.user.passport = None
        self.user.foreign_passport = None
        self.user.address = None
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            **self.user_data,
            "address": None,
	        "passport": None,
	        "foreign_passport": None
            },
            response.json()
        )

    def test_get_user_data_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_get_user_data_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )

    # PATCH METHOD
    def test_change_user_name_successful(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': 'name',
                'value': 'New name',
                'photo': self.valid_photo
                },
            format='multipart'                         
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for changing the name has been sent."},
            response.json()
        )

    def test_change_user_surname_successful(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': 'surname',
                'value': 'New surname',
                'photo': self.valid_photo
                },
            format='multipart'                        
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for changing the surname has been sent."},
            response.json()
        )

    def test_change_user_patronymic_successful(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': 'patronymic',
                'value': 'New patronymic',
                'photo': self.valid_photo
                },
            format='multipart'                       
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for changing the patronymic has been sent."},
            response.json()
        )

    def test_change_user_name_task_already_stored(self):
        task = TaskFactory(
            user=self.user, 
            title="change user name", 
            status=0
        )
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': "name",
                'value': 'New name',
                'photo': self.valid_photo
                },
            format='multipart'                       
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
                "detail": f"You have already sent a request for changing the name."
            },
            response.json()
        )

    def test_change_user_surname_task_already_stored(self):
        task = TaskFactory(
            user=self.user, 
            title="change user surname", 
            status=0
        )
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': "surname",
                'value': 'New surname',
                'photo': self.valid_photo
                },
            format='multipart'                       
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
                "detail": f"You have already sent a request for changing the surname."
            },
            response.json()
        )

    def test_change_user_patronymic_task_already_stored(self):
        task = TaskFactory(
            user=self.user, 
            title="change user patronymic", 
            status=0
        )
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': "patronymic",
                'value': 'New patronymic',
                'photo': self.valid_photo
                },
            format='multipart'                       
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
                "detail": f"You have already sent a request for changing the patronymic."
            },
            response.json()
        )

    def test_change_user_data_no_pasport(self):
        self.client.force_authenticate(self.user_without_passport)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You must have an internal passport to change the data."},
            response.json()
        )

    def test_change_user_data_no_photo(self):
        response = self.client.patch(
            path=self.path,
            data={
                'field': "name",
                'value': "Sasha"
            },
            format='json'                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "photo_errors": {"photo": ["No file was submitted."]}
            },
            response.json()
        )

    def test_change_user_data_no_user_fields(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={'photo': self.valid_photo},
            format='multipart'                     
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
                "user_errors": {"field": ["This field is required."],
                                "value": ["This field is required."]
                                }
            },
            response.json()
        )

    def test_change_user_data_incorrect_field(self):
        invalid_field = "first_name"
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': invalid_field,
                'value': "Sasha",
                'photo': self.valid_photo
            },
            format='multipart'                    
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
                "user_errors": {"field": [f"\"{invalid_field}\" is not a valid choice."]}
            },
            response.json()
        )

    def test_change_user_data_blank_value(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('change_userdata.jpg', f.read(), content_type='image/jpg')
        response = self.client.patch(
            path=self.path,
            data={
                'field': 'name',
                'value': '',
                'photo': self.valid_photo
                },
            format='multipart'                      
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
                "user_errors": {"value": ["This field may not be blank."]}
            },
            response.json()
        )

    def test_change_user_data_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_change_user_data_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )
