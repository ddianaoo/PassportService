from django.urls import path, include
from .rest_views import (
    InternalPassportDetailAPIView,
    ForeignPassportDetailAPIView,
    GetDocumentsAPIView,
    UserAddressAPIView,
    UserDataAPIView,
    VisaViewSet,
    TaskListForUserViewSet
)
from rest_framework import routers


r = routers.DefaultRouter()
r.register(r'visas', VisaViewSet, basename='visas')
r.register(r'tasks', TaskListForUserViewSet, basename='tasks')


urlpatterns = [
    path('', GetDocumentsAPIView.as_view(), name='get_my_documents_api'),
    path('internal-passport/', InternalPassportDetailAPIView.as_view(), name='my_internal_passport_api'),
    path('foreign-passport/', ForeignPassportDetailAPIView.as_view(), name='my_foreign_passport_api'),
    path('address/', UserAddressAPIView.as_view(), name='my_address_api'),
    path('user-data/', UserDataAPIView.as_view(), name='my_address_api'),
    path('', include(r.urls)),
]
