from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from passports.utils import COUNTRY_CHOICES_DICT
import datetime
from django.utils import timezone
from passports.factories import AddressFactory, PassportFactory
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os


class InternalPassportDetailAPITests(APITestCase):
    def setUp(self):
        self.path = "/api/my-documents/internal-passport/"

        address = AddressFactory(
            country_code="UA",
            region="Kharkiv region",
            settlement="Kharkiv",
            street="Zoryana 4",
            apartments="88",
            post_code=61070
        )
        passport = PassportFactory(
            photo='',
        )
        self.user = CustomUserFactory(
            email="test@test.com",
            address=address,
            passport=passport,
            foreign_passport=None,
        )
        self.user_nationality = COUNTRY_CHOICES_DICT[self.user.nationality]
        self.user_without_passport = CustomUserFactory(
            email="test2@test.com",
            passport=None,
            foreign_passport=None,
        )
        self.client.force_authenticate(self.user_without_passport)

        self.valid_address_data = {
	        "country_code": "UA",
	        "region": "Kharkiv region",
	        "settlement": "Kharkiv",
	        "street": "Zoryana 4",
	        "apartments": "11",
	        "post_code": 61070
        }
        self.image_path = os.path.join(settings.MEDIA_ROOT, 'tests/create_ip.png')
        self.loss_reason = "loss"
        self.expiry_reason = "expiry"

    # GET METHOD
    def test_get_internal_passport_successful(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(path=self.path)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
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
        },
            response.json(),
        )

    def test_get_internal_passport_no_data(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            {"detail": "Internal passport not found."},
            response.json(),
        )

    def test_get_internal_passport_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json(),
        )

    # POST METHOD
    def test_create_internal_passport_successful(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.post(path=self.path,
           data={
            **self.valid_address_data,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {"detail": "Your request for creating an internal passport has been sent."},
            response.json(),
        )

    def test_create_internal_passport_without_photo(self):
        response = self.client.post(
            path=self.path,
            data=self.valid_address_data,
            format='json', 
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'photo_errors': {'photo': ['No file was submitted.']}}, 
            response.json()
        ) 

    def test_create_internal_passport_incorrect_address_country_code(self):
        invalid_country_code = "Ukraine"
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.post(path=self.path,
           data={
	        "country_code": invalid_country_code,
	        "region": "Kharkiv region",
	        "settlement": "Kharkiv",
	        "street": "Zoryana 4",
	        "apartments": "11",
	        "post_code": 61070,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'address_errors': {
                'country_code': [f"\"{invalid_country_code}\" is not a valid choice."],
                }, 
            },
            response.json()
        ) 

    def test_create_internal_passport_incorrect_address_post_code(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.post(path=self.path,
           data={
	        "country_code": "UA",
	        "region": "Kharkiv region",
	        "settlement": "Kharkiv",
	        "street": "Zoryana 4",
	        "apartments": "11",
	        "post_code": 100003,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'address_errors': {
                'post_code': ["Post code must be positive and in the format xxxxx."],
                }, 
            },
            response.json()
        ) 

    def test_create_internal_passport_without_any_data(self):
        response = self.client.post(
            path=self.path,
            data={},
            format='json', 
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'address_errors': {
                'country_code': ['This field is required.'], 
                'region': ['This field is required.'], 
                'settlement': ['This field is required.'], 
                'street': ['This field is required.'], 
                'apartments': ['This field is required.'], 
                'post_code': ['This field is required.']
                }, 
            'photo_errors': {'photo': ['No file was submitted.']}
            },
            response.json()
        ) 

    def test_create_internal_passport_task_already_stored(self):
        task = TaskFactory(
            user=self.user_without_passport, 
            title='create an internal passport', 
            status=0, 
            user_data={}
        )
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You have already sent an application for the creation of an internal passport."},
            response.json(),
        )

    def test_create_internal_passport_passport_already_stored(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You already have an internal passport."},
            response.json(),
        )

    def test_create_internal_passport_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json(),
        )

    # PUT METHOD
    def test_restore_internal_passport_due_to_loss_successful(self):
        self.client.force_authenticate(self.user)
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'reason': self.loss_reason,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for restoring an internal passport due to {self.loss_reason} has been sent."},
            response.json(),
        )

    def test_restore_internal_passport_due_to_expiry_successful(self):
        self.client.force_authenticate(self.user)
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'reason': self.expiry_reason,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for restoring an internal passport due to {self.expiry_reason} has been sent."},
            response.json(),
        )

    def test_restore_internal_passport_due_to_loss_task_already_stored(self):
        task_title = f"restore an internal passport due to {self.loss_reason}"
        task = TaskFactory(
            user=self.user_without_passport, 
            title=task_title, 
            status=0, 
            user_data={}
        )
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'reason': self.loss_reason,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": f"You have already sent an application for restoring an internal passport due to {self.loss_reason}."},
            response.json(),
        )

    def test_restore_internal_passport_due_to_expiry_task_already_stored(self):
        task_title = f"restore an internal passport due to {self.expiry_reason}"
        task = TaskFactory(
            user=self.user_without_passport, 
            title=task_title, 
            status=0, 
            user_data={}
        )
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'reason': self.expiry_reason,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": f"You have already sent an application for restoring an internal passport due to {self.expiry_reason}."},
            response.json(),
        )

    def test_restore_internal_passport_no_pasport(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'reason': self.loss_reason,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You don't have an internal passport yet."},
            response.json(),
        )

    def test_restore_internal_passport_no_photo(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'reason': self.loss_reason,
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"photo": ["No file was submitted."]},
            response.json(),
        )

    def test_restore_internal_passport_no_reason(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"reason": ["This field is required."]},
            response.json(),
        )

    def test_restore_internal_passport_incorrect_reason(self):
        invalid_reason = "job"
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_ip.png', f.read(), content_type='image/png')
        response = self.client.put(path=self.path,
           data={
            'reason': invalid_reason,
            'photo': self.valid_photo
        },
           format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"reason": [f"\"{invalid_reason}\" is not a valid choice."]
            },
            response.json(),
        )

    def test_restore_internal_passport_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json(),
        )
