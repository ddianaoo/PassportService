from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os
from passports.utils import COUNTRY_CHOICES_DICT
from passports.factories import PassportFactory, ForeignPassportFactory
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY


class ForeignPassportDetailAPITests(APITestCase):
    def setUp(self):
        self.path = "/api/my-documents/foreign-passport/"

        self.user = CustomUserFactory(
            email="test@test.com",
            passport=PassportFactory(photo=''),
            foreign_passport=ForeignPassportFactory(photo=''),
        )
        self.user_nationality = COUNTRY_CHOICES_DICT[self.user.nationality]

        self.user_without_passport = CustomUserFactory(
            email="test2@test.com",
            passport=None,
            foreign_passport=None,
        )
        self.user_without_foreign_passport = CustomUserFactory(
            email="test3@test.com",
            passport=PassportFactory(photo=''),
            foreign_passport=None,
        )
        self.admin = CustomUserFactory(
            email="admin@test.com",
            address=None,
            passport=None,
            foreign_passport=None,
            is_staff=True
        )

        self.client.force_authenticate(self.user_without_foreign_passport)

        self.image_path = os.path.join(settings.MEDIA_ROOT, 'tests/create_fp.jpg')
        self.loss_reason = "loss"
        self.expiry_reason = "expiry"

    # GET METHOD
    def test_get_foreign_passport_successful(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
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
        },
            response.json()
        )

    def test_get_foreign_passport_no_data(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            {"detail": "Foreign passport not found."},
            response.json()
        )

    def test_get_foreign_passport_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_get_foreign_passport_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )

    # POST METHOD
    def test_create_foreign_passport_successful(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.post(
            path=self.path,
            data={'photo': self.valid_photo},
            format='multipart'                      
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {"detail": "Your request for creating a foreign passport has been sent."},
            response.json()
        )

    def test_create_foreign_passport_without_any_data(self):
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'photo': ['No file was submitted.']},
            response.json()
        ) 

    def test_create_foreign_passport_no_internal_passport(self):
        self.client.force_authenticate(self.user_without_passport)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You must have an internal passport to create a foreign passport."},
            response.json()
        )

    def test_create_foreign_passport_task_already_stored(self):
        task = TaskFactory(
            user=self.user_without_foreign_passport, 
            title='create a foreign passport', 
            status=0
        )
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You have already sent a request for creating a foreign passport."},
            response.json()
        )

    def test_create_foreign_passport_already_stored(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You already have a foreign passport."},
            response.json()
        )

    def test_create_foreign_passport_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_create_foreign_passport_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )

    # PUT METHOD
    def test_restore_foreign_passport_due_to_loss_successful(self):
        self.client.force_authenticate(self.user)
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.loss_reason,
                'photo': self.valid_photo
            },
            format='multipart',                         
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for restoring a foreign passport due to {self.loss_reason} has been sent."},
            response.json()
        )

    def test_restore_foreign_passport_due_to_expiry_successful(self):
        self.client.force_authenticate(self.user)
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.expiry_reason,
                'photo': self.valid_photo
            },
            format='multipart'                       
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for restoring a foreign passport due to {self.expiry_reason} has been sent."},
            response.json()
        )

    def test_restore_foreign_passport_due_to_loss_task_already_stored(self):
        self.client.force_authenticate(self.user)
        task_title = f"restore a foreign passport due to {self.loss_reason}"
        task = TaskFactory(
            user=self.user, 
            title=task_title, 
            status=0
        )
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.loss_reason,
                'photo': self.valid_photo
            },
            format='multipart'                     
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": f"You have already sent a request for restoring a foreign passport due to {self.loss_reason}."},
            response.json(),
        )

    def test_restore_foreign_passport_due_to_expiry_task_already_stored(self):
        self.client.force_authenticate(self.user)
        task_title = f"restore a foreign passport due to {self.expiry_reason}"
        task = TaskFactory(
            user=self.user, 
            title=task_title, 
            status=0
        )
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.expiry_reason,
                'photo': self.valid_photo
            },
            format='multipart'                      
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": f"You have already sent a request for restoring a foreign passport due to {self.expiry_reason}."},
            response.json()
        )

    def test_restore_foreign_passport_no_pasport(self):
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.loss_reason,
                'photo': self.valid_photo
            },
            format='multipart'                       
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You don't have a foreign passport yet."},
            response.json()
        )

    def test_restore_foreign_passport_no_photo(self):
        self.client.force_authenticate(self.user)
        response = self.client.put(
            path=self.path,
            data={'reason': self.loss_reason },
            format='json'                       
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"photo": ["No file was submitted."]},
            response.json()
        )

    def test_restore_foreign_passport_no_reason(self):
        self.client.force_authenticate(self.user)
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={'photo': self.valid_photo},
            format='multipart'                        
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"reason": ["This field is required."]},
            response.json()
        )

    def test_restore_foreign_passport_incorrect_reason(self):
        self.client.force_authenticate(self.user)
        invalid_reason = "job"
        with open(self.image_path, 'rb') as f:
            self.valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': invalid_reason,
                'photo': self.valid_photo
            },
           format='multipart'                      
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"reason": [f"\"{invalid_reason}\" is not a valid choice."]},
            response.json()
        )

    def test_restore_foreign_passport_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_restore_foreign_passport_admin_logged_in_forbidden(self):
        self.client.force_authenticate(self.admin)
        response = self.client.put(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )
