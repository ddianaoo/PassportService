from django.urls import path
from .rest_views import CreatePassportAPIView


urlpatterns = [
    path('create-passport/', CreatePassportAPIView.as_view(), name='create_passport_api'),
    # path('my-passport/', PassportRetrieveUpdateView.as_view(), name='get_ipassport_rest'),
    # path('my-passport/create/', PassportCreateView.as_view(), name='create_ipassport_rest'),
    # path('my-passport/extend/', PassportRetrieveUpdateView.as_view(), name='extend_my_passport'),
    # path('my-foreign-passport/', ForeignPassportRetrieveView.as_view(), name='my_foreign_passport'),
    # path('my-foreign-passport/create/', ForeignPassportCreateView.as_view(), name='create_my_foreign_passport'),
]
