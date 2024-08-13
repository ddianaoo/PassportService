from django.urls import path
from .rest_views import (
    InternalPassportDetailAPIView, 
    ForeignPassportDetailAPIView,
    GetDocumentsAPIView, 
)

urlpatterns = [
    path('', GetDocumentsAPIView.as_view(), name='get_my_documents_api'),
    path('internal-passport/', InternalPassportDetailAPIView.as_view(), name='my_internal_passport_api'),
    path('foreign-passport/', ForeignPassportDetailAPIView.as_view(), name='my_foreign_passport_api'),
]
