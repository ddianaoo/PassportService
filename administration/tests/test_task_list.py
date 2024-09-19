from administration.factories import TaskFactory
from administration.models import Task
from authentication.factories import CustomUserFactory
from passports.factories import AddressFactory, PassportFactory
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import ANY


class TaskListAPITests(APITestCase):
    def setUp(self):
        self.path =  "/api/staff/tasks/"

        address = AddressFactory(
            country_code="UA",
            region="Kharkiv region",
            settlement="Kharkiv",
            street="Zoryana 4",
            apartments="88",
            post_code=61070
        )
        self.updated_address = AddressFactory(
            country_code="UA",
            region="Kharkiv region",
            settlement="Kharkiv",
            street="Zoryana 4",
            apartments="88",
            post_code=61070
        )
        self.user = CustomUserFactory(
            name="name22",
            surname="surname22",
            email="test@test.com",
            address=address,
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

        self.task1 = TaskFactory(user=self.user, title="change user patronymic", status=1)
        self.task2 = TaskFactory(user=self.user,
                                title="change user name",
                                status=0,
                                user_data={
                                    "name": "Valerie", 
                                    "photo": "1-surname22-name22-change-user-name.jpg"
                                }
       )
        self.task3 = TaskFactory(user=self.user, title="change user surname", status=1)
        self.task4 = TaskFactory(user=self.user,
                                title="change user patronymic",
                                status=0,
                                user_data={
                                    "patronymic": "Ivanovna", 
                                    "photo": "1-surname22-name22-change-user-patronymic.jpg"
                                }                                
        )
        self.task5 = TaskFactory(user=self.user,
                                title="change registation address", 
                                status=1,
                                user_data={"address_id": self.updated_address.id}                              
                                )
        self.task6 = TaskFactory(user=self.user, title="create an internal passport", status=1)


        self.user_data = {'id': self.user.id,
            "name": self.user.name,  
            "surname": self.user.surname,  
            "patronymic": self.user.patronymic,  
                          'email': self.user.email,
            'sex': self.user.sex,
            "date_of_birth": str(self.user.date_of_birth),
            "place_of_birth": self.user.place_of_birth,
            'nationality': self.user.nationality,
            "record_number": self.user.record_number,
            "is_staff": self.user.is_staff,
                       'address': {
                "id": ANY,
                "country_code": self.user.address.country_code,
                "region": self.user.address.region,
                "settlement": self.user.address.settlement,
                "street": self.user.address.street,
                "apartments": self.user.address.apartments,
                "post_code": self.user.address.post_code
            }, 
                                   'passport': self.user.passport.number, 
                                   'foreign_passport': None}

    # GET LIST
    def test_get_tasks_count(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)   

    def test_get_tasks_sorting(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], "change user patronymic")
        self.assertEqual(response.data['results'][1]['title'], "change user name")
        self.assertEqual(response.data['results'][2]['title'], "create an internal passport")
        self.assertEqual(response.data['results'][3]['title'], "change registation address")
        self.assertEqual(response.data['results'][4]['title'], "change user surname")

    def test_get_tasks_exact_match(self):
        Task.objects.filter(status=1).delete()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
            'count': 2, 
            'next': None, 
            'previous': None, 
            'results': [
                {
                    'id': ANY, 
                    'user': self.user_data,
                    'user_data': {
                        'new_photo': ANY, 
                        'new_patronymic': self.task4.user_data['patronymic']
                    }, 
                    'title': self.task4.title, 
                    'status': 0, 
                    'created_at': ANY
                }, 
                {
                    'id': ANY, 
                    'user': self.user_data,
                    'user_data': {
                        'new_photo': ANY, 
                        'new_name': self.task2.user_data['name']
                    }, 
                    'title': self.task2.title, 
                    'status': 0, 
                    'created_at': ANY
                }, 
            ]
        }, 
        response.json())
        # print(response.json())
        self.assertEqual(len(response.data['results']), 2)


    def test_task_filtering_status_zero_successful(self):
        response = self.client.get(self.path, {'status': 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_task_filtering_status_one_successful(self):
        response = self.client.get(self.path, {'status': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 4)

    def test_task_filtering_status_two_successful(self):
        response = self.client.get(self.path, {'status': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_task_filtering_status_incorrect(self):
        response = self.client.get(self.path, {'status': 3})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({
	        "status": ["Select a valid choice. 3 is not one of the available choices."]
            },                       
            response.json()
        )

    def test_task_filtering_title_create_foreign_passport_no_data_successful(self):
        response = self.client.get(self.path, {'title': 'create-a-foreign-passport'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_task_filtering_title_change_name_successful(self):
        response = self.client.get(self.path, {'title': 'change-user-name'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_task_filtering_title_change_patronymic_successful(self):
        response = self.client.get(self.path, {'title': 'change-user-patronymic'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_task_filtering_title_change_patronymic_with_spaces(self):
        response = self.client.get(self.path, {'title': 'change user patronymic'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({'detail': 'Spaces are not allowed in the title filter.'}, response.json())

    def test_task_filtering_title_incorrect(self):
        response = self.client.get(self.path, {'title': 'passport'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual({'detail': 'Invalid title.'}, response.json())        

    def test_task_filtering_title_and_status_successful(self):
        response = self.client.get(self.path, {'status': 0, 'title': 'change-user-patronymic'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)


    def test_get_tasks_pagination_first_page(self):
        response = self.client.get(self.path, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['previous'])
        self.assertIsNotNone(response.data['next'])

    def test_get_tasks_pagination_second_page(self):
        response = self.client.get(self.path, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIsNotNone(response.data['previous'])
        self.assertIsNone(response.data['next'])

    def test_get_tasks_pagination_invalid_page(self):
        response = self.client.get(self.path, {'page': 10})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({
	        	"detail": "Invalid page."
            },      
            response.json()                 
        )

    def test_get_tasks_empty_pagination(self):
        Task.objects.all().delete()
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
        self.assertIsNone(response.data.get('previous'))
        self.assertIsNone(response.data.get('next'))        


    def test_get_tasks_user_no_access(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({
	        "detail": "You do not have permission to perform this action."
            },
            response.json()
        )

    def test_get_tasks_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )


    # GET DETAIL
    def test_get_detail_task_successful(self):
        self.maxDiff = None
        Task.objects.exclude(title="change registation address").delete()
        response = self.client.get(path=f"{self.path}{self.task5.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual({
                    'id': ANY, 
                    'user': self.user_data,
                    'user_data': {
                        'new_address': {
                            'apartments':  self.updated_address.apartments,
                            'country_code': self.updated_address.country_code,
                            'id': self.updated_address.id,
                            'post_code': self.updated_address.post_code,
                            'region': self.updated_address.region,
                            'settlement': self.updated_address.settlement,
                            'street': self.updated_address.street
                        }
                    }, 
                    'title': self.task5.title, 
                    'status': 1, 
                    'created_at': ANY
        }, 
        response.json())

    def test_get_detail_task_not_found(self):
        response = self.client.get(path=f"{self.path}100/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual({
	        "detail": "No Task matches the given query."
            },
            response.json()
        )

    def test_get_detail_task_user_no_access(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(path=f"{self.path}{self.task5.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual({
	        "detail": "You do not have permission to perform this action."
            },
            response.json()
        )

    def test_get_detail_task_not_logged_in(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(path=f"{self.path}{self.task5.pk}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            {"detail": "Authentication credentials were not provided."},
            response.json()
        )

    def test_get_detail_task_patch_method_not_allowed(self):
        response = self.client.patch(path=f"{self.path}{self.task5.pk}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            {"detail": "Method \"PATCH\" not allowed."},
            response.json()
        )

    def test_get_detail_task_put_method_not_allowed(self):
        response = self.client.put(path=f"{self.path}{self.task5.pk}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            {"detail": "Method \"PUT\" not allowed."},
            response.json()
        )        

    def test_get_detail_task_delete_method_not_allowed(self):
        response = self.client.delete(path=f"{self.path}{self.task5.pk}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(
            {"detail": "Method \"DELETE\" not allowed."},
            response.json()
        ) 
