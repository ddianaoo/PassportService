from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from passports.factories import AddressFactory, PassportFactory


class ChangeAddressByStaffAPITests(APITestCase):
    def setUp(self):
        self.path =  "/api/staff/change-address/"

        self.address = AddressFactory(
            country_code="UA",
            region="Kharkiv region",
            settlement="Kharkiv",
            street="Zoryana 48",
            apartments="88",
            post_code=61070
        )
        self.updated_address = AddressFactory(
            country_code="UA",
            region="Lviv region",
            settlement="Lviv",
            street="Shevchenko 12",
            apartments="45",
            post_code=45678
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
        self.task = TaskFactory(user=self.user,
                                title="change registation address", 
                                status=0,
                                user_data={"address_id": self.updated_address.id}                              
        )


    def test_change_address_successful(self):
        response = self.client.patch(path=f"{self.path}{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({"detail": "The registration address has been successfully updated."},
            response.json()
        )
        self.user.refresh_from_db()
        self.task.refresh_from_db()
        self.assertEqual(self.user.address.id, self.updated_address.id)
        self.assertEqual(self.task.status, 1)

    def test_change_address_task_already_processed(self):
        task_done = TaskFactory(user=self.user,
                                title="change registation address", 
                                status=1,
                                user_data={"address_id": self.updated_address.id}                              
        )
        response = self.client.patch(path=f"{self.path}{task_done.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "detail": "This user's request has already been processed."},
            response.json()
        )

    def test_change_address_wrong_task(self):
        wrong_task = TaskFactory(user=self.user,
                                title="create an internal passport",
                                status=0,
                                user_data={
                                    "address_id": self.updated_address.id, 
                                    "photo": "1-surname22-name22-create-an-internal-passport.jpg"
                                }
       )
        response = self.client.patch(path=f"{self.path}{wrong_task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({
            "detail": "The task with this id and title wasn`t found."
            },
            response.json()
        )

    def test_change_address_incorrect(self):
        incorrect_task = TaskFactory(user=self.user, 
                                    title="change registation address", 
                                    status=0,
                                    user_data={"address_id": 999}
                                    )
        response = self.client.patch(path=f"{self.path}{incorrect_task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({'detail': 'No Address matches the given query.'}, response.json())


    def test_change_address_task_not_found(self):
        response = self.client.patch(path=f"{self.path}100/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({
	        "detail": "No Task matches the given query."
            },
            response.json()
        )

    def test_change_address_user_no_access(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(path=f"{self.path}{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({
	        "detail": "You do not have permission to perform this action."
            },
            response.json()
        )

    def test_change_address_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(path=f"{self.path}{self.task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )
