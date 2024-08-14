from django.urls import path, include
from .rest_views import (TaskListAPIView, 
                         CreateInternalPassportByStaffAPIView, 
                         CreateForeignPassportForUserAPIView,
                         RestoreInternalPassportAPIView,
                         RestoreForeignPassportAPIView,
                         ChangeAddressForUserAPIView
)                         
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'tasks', TaskListAPIView, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('create-internal-passport/<int:task_pk>/', CreateInternalPassportByStaffAPIView.as_view(), name='create_ipassport_s_api'),
    path('create-foreign-passport/<int:task_pk>/', CreateForeignPassportForUserAPIView.as_view(), name='create_fpassport_s_api'),
    path('restore-internal-passport/<int:task_pk>/', RestoreInternalPassportAPIView.as_view(), name='restore_ipassport_s_api'),
    path('restore-foreign-passport/<int:task_pk>/', RestoreForeignPassportAPIView.as_view(), name='restore_fpassport_s_api'),
    path('change-address/<int:task_pk>/', ChangeAddressForUserAPIView.as_view(), name='change_address_s_api'),    
]
