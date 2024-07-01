from django.urls import path
from .views import TaskListView, create_passport, create_fpassport, restore_passport


urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='tasks_list'),
    path('create-passport/<int:pk>/', create_passport, name='create_passport_s'),
    path('create-foreign-passport/<int:pk>/', create_fpassport, name='create_fpassport_s'),
    path('restore-passport/<int:pk>/', restore_passport, name='restore_passport_s'),
]
