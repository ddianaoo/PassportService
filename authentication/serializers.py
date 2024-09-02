from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers

from authentication.models import CustomUser
from passports.serializers import AddressSerializer


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = ('name', 'surname', 'patronymic', 'email', 'password1', 
                  'password2', 'sex', 'date_of_birth', 'place_of_birth', 'nationality')

                  
class UserListSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = CustomUser
        fields = ('id', 'name', 'surname', 'patronymic', 'email', 
                   'sex', 'date_of_birth', 'place_of_birth', 'nationality',
                   'record_number', 'address', 'passport', 'foreign_passport')


class ChangeUserDataSerializer(serializers.Serializer):
    field = serializers.ChoiceField(choices=[('name', 'name'), 
                                             ('surname', 'surname'),
                                             ('patronymic', 'patronymic'),
                                             ])
    value = serializers.CharField()
