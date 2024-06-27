from django.urls import path
from .views import main_page, create_passport, get_documents


urlpatterns = [
    path('', main_page, name='home'),
    path('create-passport/', create_passport, name='create_passport_u'),
    path('my-documents/', get_documents, name='get_documents'),
]
