from django.urls import path
from .views import main_page, create_passport, create_fpassport, get_documents, restore_passport_loss, restore_passport_expiry


urlpatterns = [
    path('', main_page, name='home'),
    path('create-passport/', create_passport, name='create_passport_u'),
    path('create-fpassport/', create_fpassport, name='create_fpassport_u'),
    path('my-documents/', get_documents, name='get_documents'),
    path('restore-passport-loss/', restore_passport_loss, name='restore_passport_loss_u',),
    path('restore-passport-expiry/', restore_passport_expiry, name='restore_passport_expiry_u',),
]
