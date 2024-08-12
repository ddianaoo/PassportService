from django.urls import path
from .rest_views import (
    CreatePassportAPIView, 
    CreateForeignPassportAPIView,
    GetDocumentsAPIView,
    GetInternalPassportAPIView,
    GetForeignPassportAPIView,    
)

urlpatterns = [
    path('create-internal-passport/', CreatePassportAPIView.as_view(), name='create_internal_passport_api'),
    path('create-foreign-passport/', CreateForeignPassportAPIView.as_view(), name='create_foreign_passport_api'),
    path('my-documents/', GetDocumentsAPIView.as_view(), name='get_my_documents_api'),
    path('my-documents/internal-passport/', GetInternalPassportAPIView.as_view(), name='get_my_internal_passport_api'),
    path('my-documents/foreign-passport/', GetForeignPassportAPIView.as_view(), name='get_my_foreign_passport_api'),
]
