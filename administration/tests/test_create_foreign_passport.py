from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY

from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from passports.factories import AddressFactory, PassportFactory


class CreateForeignPassportByStaffAPITests(APITestCase):
    def setUp(self):
        self.path = "/api/staff/create-foreign-passport/"

        self.address = AddressFactory(
            country_code="UA",
            region="Kharkiv region",
            settlement="Kharkiv",
            street="Zoryana 48",
            apartments="88",
            post_code=61070
        )
        self.user = CustomUserFactory(
            name="name22",
            surname="surname22",
            email="test@test.com",
            address=self.address,
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
        self.client.force_authenticate(self.admin)

        self.task = TaskFactory(
            user=self.user,
            title="create a foreign passport",
            status=0,
            user_data={
                "photo": "1-surname22-name22-create-a-foreign-passport.jpg"
            }
        )
        self.valid_data = {
            "authority": 6666,
            "date_of_issue": str(timezone.now().date()),
            "date_of_expiry": str(timezone.now().date() + timezone.timedelta(days=365 * 10 + 2))
        }

    def test_create_foreign_passport_successful(self):
        response = self.client.post(
            path=f"{self.path}{self.task.pk}/",
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {
                "number": ANY,
                "authority": self.valid_data['authority'],
                "date_of_issue": self.valid_data['date_of_issue'],
                "date_of_expiry": self.valid_data['date_of_expiry'],
                "photo": ANY
            },
            response.json()
        )
        self.user.refresh_from_db()
        self.task.refresh_from_db()
        self.assertEqual(self.user.address.id, self.address.id)
        self.assertEqual(self.user.foreign_passport.number, response.data['number'])
        self.assertEqual(self.task.status, 1)

    def test_create_foreign_passport_task_already_processed(self):
        task_done = TaskFactory(
            user=self.user,
            title="create a foreign passport",
            status=1,
            user_data={
                "photo": "1-surname22-name22-create-a-foreign-passport.jpg"
            }
        )
        response = self.client.post(
            path=f"{self.path}{task_done.pk}/",
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "detail": "Request has already been processed."},
            response.json()
        )

    def test_create_foreign_passport_wrong_task(self):
        wrong_task = TaskFactory(
            user=self.user,
            title="change registation address",
            status=0,
            user_data={"address_id": self.address.id}
        )
        response = self.client.post(
            path=f"{self.path}{wrong_task.pk}/",
            data=self.valid_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            {"detail": "The task with this id and title wasn`t found."},
            response.json()
        )

    def test_create_foreign_passport_without_authority(self):
        response = self.client.post(
            path=f"{self.path}{self.task.pk}/",
            data={
                "date_of_issue": self.valid_data['date_of_issue'],
                "date_of_expiry": self.valid_data['date_of_expiry']
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {'authority': ['This field is required.']},
            response.json()
        )

    def test_create_foreign_passport_authority_incorrect(self):
        response = self.client.post(
            path=f"{self.path}{self.task.pk}/",
            data={
                "authority": 10,
                "date_of_issue": self.valid_data['date_of_issue'],
                "date_of_expiry": self.valid_data['date_of_expiry']
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"authority": ["Authority must be in the format xxxx."]}, response.json())

    def test_create_foreign_passport_date_format_incorrect(self):
        response = self.client.post(
            path=f"{self.path}{self.task.pk}/",
            data={
                "authority": self.valid_data['authority'],
                "date_of_issue": "08-18-2024",
                "date_of_expiry": self.valid_data['date_of_expiry']
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                "date_of_issue": ['Date has wrong format. Use one of these formats instead: YYYY-MM-DD.']
            },
            response.json()
        )

    def test_create_foreign_passport_date_of_issue_incorrect(self):
        response = self.client.post(
            path=f"{self.path}{self.task.pk}/",
            data={
                "authority": self.valid_data['authority'],
                "date_of_issue": "2024-08-18",
                "date_of_expiry": self.valid_data['date_of_expiry']
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"date_of_issue": ["Issue date must be at least today."]}, response.json())

    def test_create_foreign_passport_date_of_expiry_incorrect(self):
        response = self.client.post(
            path=f"{self.path}{self.task.pk}/",
            data={
                "authority": self.valid_data['authority'],
                "date_of_issue": self.valid_data['date_of_issue'],
                "date_of_expiry": "2024-10-19"
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                "date_of_expiry": ["The expiry date must be in 10 years since today."]
            },
            response.json()
        )

    def test_create_foreign_passport_no_data(self):
        response = self.client.post(path=f"{self.path}{self.task.pk}/", data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            {
                'authority': ['This field is required.'],
                'date_of_expiry': ['This field is required.'],
                'date_of_issue': ['This field is required.']
            },
            response.json()
        )

    def test_create_foreign_passport_task_not_found(self):
        response = self.client.post(path=f"{self.path}100/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            {"detail": "No Task matches the given query."},
            response.json()
        )

    def test_create_foreign_passport_user_no_access(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(path=f"{self.path}{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            {"detail": "You do not have permission to perform this action."},
            response.json()
        )

    def test_create_foreign_passport_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(path=f"{self.path}{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )
