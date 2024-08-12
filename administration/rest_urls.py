from django.urls import path, include
from .rest_views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'tasks', TaskListAPIView, basename='task')

urlpatterns = [
    # path('tasks/', TaskListAPIView.as_view(), name='api_tasks_list'),
    path('', include(router.urls)),
]
