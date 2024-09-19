from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .rest_views import (
    TaskListAPIView,
    CreateInternalPassportAPIView,
    RestoreInternalPassportAPIView,
    CreateForeignPassportAPIView,
    RestoreForeignPassportAPIView,
    ChangeUserAddressAPIView,
    ChangeUserFieldAPIView,
    CreateVisaAPIView,
    ExtendVisaExtentionAPIView,
    RejectTaskAPIView,
    RestoreVisaAPIView
)


router = DefaultRouter()
router.register(r'tasks', TaskListAPIView, basename='task')

urlpatterns = [
    path('', include(router.urls)),
    path('create-internal-passport/<int:task_pk>/', CreateInternalPassportAPIView.as_view(), name='create_ipassport_s_api'),
    path('create-foreign-passport/<int:task_pk>/', CreateForeignPassportAPIView.as_view(), name='create_fpassport_s_api'),
    path('restore-internal-passport/<int:task_pk>/', RestoreInternalPassportAPIView.as_view(), name='restore_ipassport_s_api'),
    path('restore-foreign-passport/<int:task_pk>/', RestoreForeignPassportAPIView.as_view(), name='restore_fpassport_s_api'),
    path('change-address/<int:task_pk>/', ChangeUserAddressAPIView.as_view(), name='change_address_s_api'),
    path('change-data/<int:task_pk>/', ChangeUserFieldAPIView.as_view(), name='change_data_s_api'),
    path('create-visa/<int:task_pk>/', CreateVisaAPIView.as_view(), name='create_visa_s_api'),
    path('extend-visa/<int:task_pk>/', ExtendVisaExtentionAPIView.as_view(), name='extend_visa_s_api'),
    path('restore-visa/<int:task_pk>/', RestoreVisaAPIView.as_view(), name='restore_visa_s_api'),
    path('reject-task/<int:task_pk>/', RejectTaskAPIView.as_view(), name='reject_task_s_api'),
]
