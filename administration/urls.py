from django.urls import path
from .views import (TaskListView, 
                    create_ipassport_for_user, 
                    create_fpassport_for_user, 
                    restore_ipassport_for_user, 
                    restore_fpassport_for_user,
                    change_address_for_user,
                    change_name_for_user,
                    change_surname_for_user, 
                    change_patronymic_for_user
)


urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='tasks_list'),
    path('create-passport/<int:task_pk>/', create_ipassport_for_user, name='create_passport_s'),
    path('create-foreign-passport/<int:task_pk>/', create_fpassport_for_user, name='create_fpassport_s'),
    path('restore-passport/<int:task_pk>/', restore_ipassport_for_user, name='restore_passport_s'),
    path('restore-fpassport/<int:task_pk>/', restore_fpassport_for_user, name='restore_fpassport_s'),
    path('change-address/<int:task_pk>/', change_address_for_user, name='change_address_s'),
    path('change-name/<int:task_pk>/', change_name_for_user, name='change_name_s'),
    path('change-surname/<int:task_pk>/', change_surname_for_user, name='change_surname_s'),
    path('change-patronymic/<int:task_pk>/', change_patronymic_for_user, name='change_patronymic_s'),
]
