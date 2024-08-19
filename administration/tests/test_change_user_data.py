from administration.factories import TaskFactory
from authentication.factories import CustomUserFactory
from django.utils import timezone
from passports.factories import AddressFactory, PassportFactory, ForeignPassportFactory, VisaFactory
from passports.models import Visa
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY


class ChangeUserDataByStaffAPITests(APITestCase):
    def setUp(self):
        self.path =  "/api/staff/change-data/"

        self.address = AddressFactory(
            country_code="UA",
            region="Kharkiv region",
            settlement="Kharkiv",
            street="Zoryana 48",
            apartments="88",
            post_code=61070
        )     
        self.internal_passport1 = PassportFactory(photo='')  
        self.user1 = CustomUserFactory(
            name="name22",
            surname="surname22",
            email="test1@test.com",
            address=self.address,
            passport=self.internal_passport1,
            foreign_passport=None,
        )
        self.internal_passport2 = PassportFactory(photo='')  
        self.foreign_passport2 = ForeignPassportFactory(photo='')
        self.visa = VisaFactory(foreign_passport=self.foreign_passport2)
        self.user2 = CustomUserFactory(
            name="name23",
            surname="surname23",
            email="test2@test.com",
            address=self.address,
            passport=self.internal_passport2,
            foreign_passport=self.foreign_passport2
        )
        self.admin = CustomUserFactory(
            email="admin@test.com",
            address=None,
            passport=None,
            foreign_passport=None,
            is_staff=True
        )
        self.client.force_authenticate(self.admin)

        self.wrong_task_title = TaskFactory(user=self.user1,
                                title="create an internal passport",
                                status=0,
                                user_data={
                                    "address_id": AddressFactory().id, 
                                    "photo": "1-surname22-name22-create-an-internal-passport.jpg"
                                }
       )
        self.task_name1 = TaskFactory(user=self.user1,
                                title="change user name", 
                                status=0,
                                user_data={
                                    "name": "Kate", 
                                    "photo": "1-surname22-name22-change-data.jpg"
                                }                             
                                )
        self.task_surname1 = TaskFactory(user=self.user1,
                                title="change user surname", 
                                status=0,
                                user_data={
                                    "surname": "White", 
                                    "photo": "1-surname22-name22-change-data.jpg"
                                }                             
                                )
        self.task_patronymic1 = TaskFactory(user=self.user1,
                                title="change user patronymic", 
                                status=0,
                                user_data={
                                    "patronymic": "Ivanovna", 
                                    "photo": "1-surname22-name22-change-data.jpg"
                                }                             
                                )
        self.task_name2 = TaskFactory(user=self.user2,
                                title="change user name", 
                                status=0,
                                user_data={
                                    "name": "Kate", 
                                    "photo": "1-surname22-name22-change-data.jpg"
                                }                             
                                )
        self.task_surname2 = TaskFactory(user=self.user2,
                                title="change user surname", 
                                status=0,
                                user_data={
                                    "surname": "White", 
                                    "photo": "1-surname22-name22-change-data.jpg"
                                }                             
                                )
        self.task_patronymic2 = TaskFactory(user=self.user2,
                                title="change user patronymic", 
                                status=0,
                                user_data={
                                    "patronymic": "Ivanovna", 
                                    "photo": "1-surname22-name22-change-data.jpg"
                                }                             
                                )
        self.valid_data = {
                "authority": 6666,
                "date_of_issue": str(timezone.now().date()),
			    "date_of_expiry": str(timezone.now().date() + timezone.timedelta(days=365*10+2))
            }


# INTERNAL PASSPORT ONLY
    def test_change_user_data_in_internal_passport_name_successful(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name1.pk}/",
            data={"internal_passport": self.valid_data},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({"detail": "The user name has been successfully updated."}, response.json())
        self.user1.refresh_from_db()
        self.task_name1.refresh_from_db()
        self.assertNotEqual(self.user1.passport.number, self.internal_passport1.number)
        self.assertEqual(self.user1.name, self.task_name1.user_data['name'])
        self.assertEqual(self.task_name1.status, 1)

    def test_change_user_data_in_internal_passport_surname_successful(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_surname1.pk}/",
            data={"internal_passport": self.valid_data},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({"detail": "The user surname has been successfully updated."}, response.json())
        self.user1.refresh_from_db()
        self.task_surname1.refresh_from_db()
        self.assertNotEqual(self.user1.passport.number, self.internal_passport1.number)
        self.assertEqual(self.user1.surname, self.task_surname1.user_data['surname'])
        self.assertEqual(self.task_surname1.status, 1)

    def test_change_user_data_in_internal_passport_patronymic_successful(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_patronymic1.pk}/",
            data={"internal_passport": self.valid_data},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({"detail": "The user patronymic has been successfully updated."}, response.json())
        self.user1.refresh_from_db()
        self.task_patronymic1.refresh_from_db()
        self.assertNotEqual(self.user1.passport.number, self.internal_passport1.number)
        self.assertEqual(self.user1.patronymic, self.task_patronymic1.user_data['patronymic'])
        self.assertEqual(self.task_patronymic1.status, 1)


    def test_change_user_data_in_internal_passport_without_authority(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name1.pk}/",
            data={
                "internal_passport":{
	                "date_of_issue": self.valid_data['date_of_issue'],
	                "date_of_expiry": self.valid_data['date_of_expiry']
            }},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({'authority': ['This field is required.']}, response.json())

    def test_change_user_data_in_internal_passport_authority_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name1.pk}/",
            data={
                "internal_passport":{
                    "authority": 10,
	                "date_of_issue": self.valid_data['date_of_issue'],
	                "date_of_expiry": self.valid_data['date_of_expiry']
            }},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"authority": ["Authority must be in the format xxxx."]}, response.json())

    def test_change_user_data_in_internal_passport_date_format_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name1.pk}/",
            data={
                "internal_passport":{
                    "authority": self.valid_data['authority'],
                    "date_of_issue": "08-18-2024",
			        "date_of_expiry": self.valid_data['date_of_expiry']
            }},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "date_of_issue": 
                ['Date has wrong format. Use one of these formats instead: YYYY-MM-DD.']
            }, 
            response.json()
        )

    def test_change_user_data_in_internal_passport_date_of_issue_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name1.pk}/",
            data={
                "internal_passport":{
                    "authority": self.valid_data['authority'],
                    "date_of_issue": "2024-08-18",
			        "date_of_expiry": self.valid_data['date_of_expiry']
            }},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({"date_of_issue": ["Issue date must be at least today."]}, response.json())

    def test_change_user_data_in_internal_passport_date_of_expiry_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name1.pk}/",
            data={
                "internal_passport":{
                    "authority": self.valid_data['authority'],
                    "date_of_issue": self.valid_data['date_of_issue'],
			        "date_of_expiry": "2024-10-19"
            }},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "date_of_expiry": ["The expiry date must be in 10 years since today."]
            }, 
            response.json()
        )

    def test_change_user_data_in_internal_passport_no_data(self):
        response = self.client.patch(path=f"{self.path}{self.task_name1.pk}/", data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({'non_field_errors': ['No data provided']}, response.json())


# BOTH PASSPORTS
    def test_change_user_data_in_both_passports_name_successful(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name2.pk}/",
            data={
                "internal_passport": self.valid_data,
                "foreign_passport": self.valid_data
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({"detail": "The user name has been successfully updated."}, response.json())
        self.user2.refresh_from_db()
        self.task_name2.refresh_from_db()
        self.assertNotEqual(self.user2.passport.number, self.internal_passport2.number)
        self.assertNotEqual(self.user2.foreign_passport.number, self.foreign_passport2.number)
        visas = Visa.objects.all()
        self.assertFalse(visas)
        self.assertEqual(self.user2.name, self.task_name2.user_data['name'])
        self.assertEqual(self.task_name2.status, 1)

    def test_change_user_data_in_both_passports_surname_successful(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_surname2.pk}/",
            data={
                "internal_passport": self.valid_data,
                "foreign_passport": self.valid_data
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({"detail": "The user surname has been successfully updated."}, response.json())
        self.user2.refresh_from_db()
        self.task_surname2.refresh_from_db()
        self.assertNotEqual(self.user2.passport.number, self.internal_passport2.number)
        self.assertNotEqual(self.user2.foreign_passport.number, self.foreign_passport2.number)
        visas = Visa.objects.all()
        self.assertFalse(visas)
        self.assertEqual(self.user2.surname, self.task_surname2.user_data['surname'])
        self.assertEqual(self.task_surname2.status, 1)

    def test_change_user_data_in_both_passports_patronymic_successful(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_patronymic2.pk}/",
            data={
                "internal_passport": self.valid_data,
                "foreign_passport": self.valid_data
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({"detail": "The user patronymic has been successfully updated."}, response.json())
        self.user2.refresh_from_db()
        self.task_patronymic2.refresh_from_db()
        self.assertNotEqual(self.user2.passport.number, self.internal_passport2.number)
        self.assertNotEqual(self.user2.foreign_passport.number, self.foreign_passport2.number)
        visas = Visa.objects.all()
        self.assertFalse(visas)
        self.assertEqual(self.user2.patronymic, self.task_patronymic2.user_data['patronymic'])
        self.assertEqual(self.task_patronymic2.status, 1)


    def test_change_user_data_in_both_passports_without_authority(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name2.pk}/",
            data={
                "internal_passport":{
	                "date_of_issue": self.valid_data['date_of_issue'],
	                "date_of_expiry": self.valid_data['date_of_expiry']
                },
                "foreign_passport": self.valid_data
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            'internal_passport': {'authority': ['This field is required.']}
            }, 
            response.json()
        )

    def test_change_user_data_in_both_passports_authority_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name2.pk}/",
            data={
                "internal_passport": self.valid_data,
                "foreign_passport":{
                    "authority": 10,
	                "date_of_issue": self.valid_data['date_of_issue'],
	                "date_of_expiry": self.valid_data['date_of_expiry']
            }},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            'foreign_passport': {"authority": ["Authority must be in the format xxxx."]}
            }, 
            response.json()
        )

    def test_change_user_data_in_both_passports_date_format_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name2.pk}/",
            data={
                "internal_passport":{
                    "authority": self.valid_data['authority'],
                    "date_of_issue": "08-18-2024",
			        "date_of_expiry": self.valid_data['date_of_expiry']
                }, 
                "foreign_passport": self.valid_data
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "internal_passport": 
                {
                    "date_of_issue": ['Date has wrong format. Use one of these formats instead: YYYY-MM-DD.']
                }
            }, 
            response.json()
        )

    def test_change_user_data_in_both_passports_date_of_issue_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name2.pk}/",
            data={
                "internal_passport": {
                    "authority": self.valid_data['authority'],
                    "date_of_issue": "2024-08-18",
			        "date_of_expiry": self.valid_data['date_of_expiry']
                }, 
                "foreign_passport": self.valid_data
                },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "internal_passport": {"date_of_issue": ["Issue date must be at least today."]}
            }, 
            response.json())

    def test_change_user_data_in_both_passports_date_of_expiry_incorrect(self):
        response = self.client.patch(
            path=f"{self.path}{self.task_name2.pk}/",
            data={
                "internal_passport":{
                    "authority": self.valid_data['authority'],
                    "date_of_issue": self.valid_data['date_of_issue'],
			        "date_of_expiry": "2024-10-19"
                },
                "foreign_passport": self.valid_data
                },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "internal_passport":
                {"date_of_expiry": ["The expiry date must be in 10 years since today."]}
            }, 
            response.json()
        )

    def test_change_user_data_in_both_passports_no_data(self):
        response = self.client.patch(path=f"{self.path}{self.task_name2.pk}/", data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            'internal_passport': {'non_field_errors': ['No data provided']}, 
            'foreign_passport': {'non_field_errors': ['No data provided']}
            },
            response.json()
        )


    def test_change_user_data_user_doesnt_have_passport(self):
        self.user1.passport = None
        self.user1.save()
        response = self.client.patch(path=f"{self.path}{self.task_name1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "detail": "Before updating the name, the user must have an internal passport."},
            response.json()
        )

    def test_change_user_data_task_already_processed(self):
        self.task_name1.status = 1
        self.task_name1.save()
        response = self.client.patch(path=f"{self.path}{self.task_name1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
            "detail": "This user's request has already been processed."},
            response.json()
        )

    def test_change_user_data_wrong_task(self):
        response = self.client.patch(path=f"{self.path}{self.wrong_task_title.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({
            "detail": "The task with this id and title wasn`t found."
            },
            response.json()
        )


    def test_change_user_data_task_not_found(self):
        response = self.client.patch(path=f"{self.path}100/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({
	        "detail": "No Task matches the given query."
            },
            response.json()
        )

    def test_change_user_data_user_no_access(self):
        self.client.force_authenticate(self.user1)
        response = self.client.patch(path=f"{self.path}{self.task_name1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({
	        "detail": "You do not have permission to perform this action."
            },
            response.json()
        )

    def test_change_user_data_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.patch(path=f"{self.path}{self.task_name1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )
