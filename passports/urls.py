from django.urls import path
from .views import (main_page, 
                    create_passport, 
                    create_fpassport, 
                    get_documents, 
                    restore_passport_loss, 
                    restore_passport_expiry, 
                    restore_fpassport_loss,
                    restore_fpassport_expiry,
                    change_address,
)


urlpatterns = [
    path('', main_page, name='home'),
    path('create-passport/', create_passport, name='create_passport_u'),
    path('create-fpassport/', create_fpassport, name='create_fpassport_u'),
    path('my-documents/', get_documents, name='get_documents'),
    path('restore-passport-loss/', restore_passport_loss, name='restore_passport_loss_u',),
    path('restore-passport-expiry/', restore_passport_expiry, name='restore_passport_expiry_u',),
    path('restore-fpassport-loss/', restore_fpassport_loss, name='restore_fpassport_loss_u',),
    path('restore-fpassport-expiry/', restore_fpassport_expiry, name='restore_fpassport_expiry_u',),
    path('change-address/', change_address, name='change_address_u',),
]
