from django.urls import path
from .views import main_page, create_passport, create_fpassport, get_documents, restore_passport


urlpatterns = [
    path('', main_page, name='home'),
    path('create-passport/', create_passport, name='create_passport_u'),
    path('create-fpassport/', create_fpassport, name='create_fpassport_u'),
    path('my-documents/', get_documents, name='get_documents'),
    path('restore-passport/', restore_passport, name='restore_passport',)
]
