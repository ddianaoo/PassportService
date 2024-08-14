from rest_framework import serializers
from .models import Task
from authentication.serializers import UserListSerializer
from django.conf import settings
from passports.serializers import RetrieveAddressSerializer
from passports.models import Address


class UserDataSerializer(serializers.Serializer):
    photo = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    surname = serializers.CharField(required=False, allow_blank=True)
    patronymic = serializers.CharField(required=False, allow_blank=True)
    new_address = serializers.SerializerMethodField()

    def get_new_address(self, obj):
        address_id = obj.get('address_id')
        if address_id:
            address = Address.objects.get(pk=address_id)
            if address:
                return RetrieveAddressSerializer(address).data
        return None

    def to_representation(self, instance):
        """
        Customize the representation to include the absolute URL for the photo field if it exists.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if representation.get('photo') and request:
            representation['photo'] = request.build_absolute_uri(settings.MEDIA_URL + representation['photo'])
        
        if representation.get('new_address') is None:
            representation.pop('new_address', None)
        return representation
    

class TaskSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    user_data = UserDataSerializer()

    class Meta:
        model = Task
        fields = '__all__' 
