from django.urls import path, include
from .rest_views import (TaskListAPIView, 
                         CreateInternalPassportByStaffAPIView, 
                         CreateForeignPassportForUserAPIView,
)                         
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'tasks', TaskListAPIView, basename='task')

urlpatterns = [
    # path('tasks/', TaskListAPIView.as_view(), name='api_tasks_list'),
    path('', include(router.urls)),
    path('create-internal-passport/<int:task_pk>/', CreateInternalPassportByStaffAPIView.as_view(), name='create_ipassport_s_api'),
    path('create-foreign-passport/<int:task_pk>/', CreateForeignPassportForUserAPIView.as_view(), name='create_fpassport_s_api'),

]
