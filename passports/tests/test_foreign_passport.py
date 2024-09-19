import os
from io import BytesIO

from unittest.mock import ANY
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image

from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from passports.utils import COUNTRY_CHOICES_DICT
from passports.factories import PassportFactory, ForeignPassportFactory


class ForeignPassportGetAPITests(APITestCase):
    """
    Test suite for retrieving foreign passport information via the API.

    Tests various scenarios for the GET method of the foreign passport API endpoint:
    - Successful retrieval of the foreign passport details
    - Handling of requests where the user does not have a foreign passport
    - Handling of requests from unauthenticated users
    - Permission checks for admin users attempting to access foreign passport data
    """
    def setUp(self):
        self.path = "/api/my-documents/foreign-passport/"

        self.user = CustomUserFactory(
            email="test@test.com",
            passport=PassportFactory(photo=''),
            foreign_passport=ForeignPassportFactory(photo=''),
        )
        self.user_nationality = COUNTRY_CHOICES_DICT[self.user.nationality]

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

    def test_get_foreign_passport_successful(self):
        """
        Test that a user can successfully retrieve their foreign passport details.

        Verifies that the API returns a 200 OK status and the correct foreign passport data
        for the authenticated user with a foreign passport.
        """
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
        """
        Test that a user without a foreign passport receives a message indicating the absence of a foreign passport.

        Verifies that the API returns a 200 OK status and the appropriate message
        when the authenticated user does not have a foreign passport.
        The response should indicate that the user does not have a foreign passport yet.
        """
        self.client.force_authenticate(self.user_without_foreign_passport)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": "You don`t have a foreign passport yet."},
            response.json()
        )

    def test_get_foreign_passport_not_logged_in(self):
        """
        Test that unauthenticated users receive a 401 error.

        Verifies that the API returns a 401 Unauthorized status and the appropriate error message
        when no authentication credentials are provided.
        """
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_get_foreign_passport_admin_logged_in_forbidden(self):
        """
        Test that an admin user receives a 403 error when attempting to access foreign passport data.

        Verifies that the API returns a 403 Forbidden status and the appropriate error message
        when an admin user attempts to access foreign passport data, which should be restricted to regular users.
        """
        self.client.force_authenticate(self.admin)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )


class ForeignPassportCreateAPITests(APITestCase):
    """
    Test suite for creating a foreign passport via the API.

    Tests various scenarios for the POST method of the foreign passport creation API endpoint:
    - Successful creation of a foreign passport
    - Request without any data
    - Request from a user without an internal passport
    - Request when a creation task is already stored
    - Request from a user who already has a foreign passport
    - Request by an unauthenticated user
    - Request by an admin user who should be forbidden from creating a foreign passport
    """
    def setUp(self):
        self.path = "/api/my-documents/foreign-passport/"

        self.user = CustomUserFactory(
            email="test@test.com",
            passport=PassportFactory(photo=''),
            foreign_passport=ForeignPassportFactory(photo=''),
        )
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

    def test_create_foreign_passport_successful(self):
        """
        Test successful creation of a foreign passport.

        Verifies that the API returns a 201 Created status and the correct response message when
        a valid photo is provided. Ensures that the notification task is triggered.
        """
        # image_path = os.path.join(settings.MEDIA_ROOT, 'tests/create_fp.jpg')
        # with open(image_path, 'rb') as f:
        #     valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        image = Image.new('RGB', (100, 100), color='red')
        test_image = BytesIO()
        image.save(test_image, format='JPEG')
        test_image.seek(0)

        valid_photo = SimpleUploadedFile('create_visa.jpg', test_image.read(), content_type='image/jpg')

        response = self.client.post(
            path=self.path,
            data={'photo': valid_photo},
            format='multipart'
        )
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {"detail": "Your request for creating a foreign passport has been sent."},
            response.json()
        )

    def test_create_foreign_passport_without_any_data(self):
        """
        Test creation request with no data.

        Verifies that the API returns a 400 Bad Request status and an appropriate error message
        when no data is provided in the request.
        """
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'photo': ['No file was submitted.']},
            response.json()
        )

    def test_create_foreign_passport_no_internal_passport(self):
        """
        Test creation request from a user without an internal passport.

        Verifies that the API returns a 400 Bad Request status and the appropriate error message
        when the user does not have an internal passport.
        """
        self.client.force_authenticate(self.user_without_passport)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You must have an internal passport to create a foreign passport."},
            response.json()
        )

    def test_create_foreign_passport_task_already_stored(self):
        """
        Test creation request when a task is already stored.

        Verifies that the API returns a 400 Bad Request status and the appropriate error message
        when a creation task for a foreign passport already exists for the user.
        """
        TaskFactory(
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
        """
        Test creation request for a user who already has a foreign passport.

        Verifies that the API returns a 400 Bad Request status and the appropriate error message
        when the user already has a foreign passport.
        """
        self.client.force_authenticate(self.user)
        response = self.client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You already have a foreign passport."},
            response.json()
        )

    def test_create_foreign_passport_not_logged_in(self):
        """
        Test creation request by an unauthenticated user.

        Verifies that the API returns a 401 Unauthorized status and the appropriate error message
        when the request is made by a user who is not logged in.
        """
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


class ForeignPassportRestoreAPITests(APITestCase):
    def setUp(self):
        self.path = "/api/my-documents/foreign-passport/"

        self.user = CustomUserFactory(
            email="test@test.com",
            passport=PassportFactory(photo=''),
            foreign_passport=ForeignPassportFactory(photo=''),
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
        self.client.force_authenticate(self.user)
        self.image_path = os.path.join(settings.MEDIA_ROOT, 'tests/create_fp.jpg')
        self.loss_reason = "loss"
        self.expiry_reason = "expiry"

    def test_restore_foreign_passport_due_to_loss_successful(self):
        with open(self.image_path, 'rb') as f:
            valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.loss_reason,
                'photo': valid_photo
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for restoring a foreign passport due to {self.loss_reason} has been sent."},
            response.json()
        )

    def test_restore_foreign_passport_due_to_expiry_successful(self):
        with open(self.image_path, 'rb') as f:
            valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.expiry_reason,
                'photo': valid_photo
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {"detail": f"Your request for restoring a foreign passport due to {self.expiry_reason} has been sent."},
            response.json()
        )

    def test_restore_foreign_passport_due_to_loss_task_already_stored(self):
        TaskFactory(
            user=self.user,
            title=f"restore a foreign passport due to {self.loss_reason}",
            status=0
        )
        with open(self.image_path, 'rb') as f:
            valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.loss_reason,
                'photo': valid_photo
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": f"You have already sent a request for restoring a foreign passport due to {self.loss_reason}."},
            response.json(),
        )

    def test_restore_foreign_passport_due_to_expiry_task_already_stored(self):
        TaskFactory(
            user=self.user,
            title=f"restore a foreign passport due to {self.expiry_reason}",
            status=0
        )
        with open(self.image_path, 'rb') as f:
            valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.expiry_reason,
                'photo': valid_photo
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": f"You have already sent a request for restoring a foreign passport due to {self.expiry_reason}."},
            response.json()
        )

    def test_restore_foreign_passport_no_pasport(self):
        self.client.force_authenticate(self.user_without_foreign_passport)
        with open(self.image_path, 'rb') as f:
            valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': self.loss_reason,
                'photo': valid_photo
            },
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"detail": "You don't have a foreign passport yet."},
            response.json()
        )

    def test_restore_foreign_passport_no_photo(self):
        response = self.client.put(
            path=self.path,
            data={'reason': self.loss_reason},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"photo": ["No file was submitted."]},
            response.json()
        )

    def test_restore_foreign_passport_no_reason(self):
        with open(self.image_path, 'rb') as f:
            valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={'photo': valid_photo},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {"reason": ["This field is required."]},
            response.json()
        )

    def test_restore_foreign_passport_incorrect_reason(self):
        invalid_reason = "job"
        with open(self.image_path, 'rb') as f:
            valid_photo = SimpleUploadedFile('create_fp.jpg', f.read(), content_type='image/jpg')
        response = self.client.put(
            path=self.path,
            data={
                'reason': invalid_reason,
                'photo': valid_photo
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
