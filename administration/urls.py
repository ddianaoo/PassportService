from django.urls import path
from .views import get_tasks, create_passport


urlpatterns = [
    path('tasks/', get_tasks, name='tasks_list'),
    path('create-passport/<int:pk>', create_passport, name='create_passport_s')
]
