from django.urls import path
from .views import (TaskListView, 
                    create_passport, 
                    create_fpassport, 
                    restore_passport, 
                    restore_fpassport,
                    change_address,
                    change_name,
                    change_surname, 
                    change_patronymic
)


urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='tasks_list'),
    path('create-passport/<int:task_pk>/', create_passport, name='create_passport_s'),
    path('create-foreign-passport/<int:task_pk>/', create_fpassport, name='create_fpassport_s'),
    path('restore-passport/<int:task_pk>/', restore_passport, name='restore_passport_s'),
    path('restore-fpassport/<int:task_pk>/', restore_fpassport, name='restore_fpassport_s'),
    path('change-address/<int:task_pk>/', change_address, name='change_address_s'),
    path('change-name/<int:task_pk>/', change_name, name='change_name_s'),
    path('change-surname/<int:task_pk>/', change_surname, name='change_surname_s'),
    path('change-patronymic/<int:task_pk>/', change_patronymic, name='change_patronymic_s'),
]
