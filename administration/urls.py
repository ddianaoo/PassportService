from django.urls import path
from .views import (TaskListView, 
                    create_passport, 
                    create_fpassport, 
                    restore_passport, 
                    restore_fpassport,
                    restore_address,
)


urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='tasks_list'),
    path('create-passport/<int:pk>/', create_passport, name='create_passport_s'),
    path('create-foreign-passport/<int:pk>/', create_fpassport, name='create_fpassport_s'),
    path('restore-passport/<int:task_pk>/', restore_passport, name='restore_passport_s'),
    path('restore-fpassport/<int:task_pk>/', restore_fpassport, name='restore_fpassport_s'),
    path('restore-address/<int:task_pk>/', restore_address, name='restore_address_s'),
]
