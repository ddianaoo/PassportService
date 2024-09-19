from rest_framework import serializers
from django.conf import settings

from authentication.serializers import UserListSerializer
from .models import Task
from passports.serializers import AddressSerializer, VisaSerializer
from passports.models import Address, Visa


class TaskUserDataSerializer(serializers.Serializer):
    new_photo = serializers.CharField(required=False, allow_blank=True, source='photo')
    new_name = serializers.CharField(required=False, allow_blank=True, source='name')
    new_surname = serializers.CharField(required=False, allow_blank=True, source='surname')
    new_patronymic = serializers.CharField(required=False, allow_blank=True, source='patronymic')
    new_address = serializers.SerializerMethodField()

    visa_type = serializers.CharField(required=False, allow_blank=True)
    visa_country = serializers.CharField(required=False, allow_blank=True)
    visa_entry_amount = serializers.CharField(required=False, allow_blank=True)

    visa = serializers.SerializerMethodField()

    visa_extension_reason = serializers.CharField(required=False, allow_blank=True)
    visa_extension_date = serializers.DateField(required=False)

    def get_visa(self, obj):
        visa_id = obj.get('visa_id')
        if visa_id:
            visa = Visa.objects.get(pk=visa_id)
            if visa:
                return VisaSerializer(visa, context={'request': self.context.get('request')}).data
        return None

    def get_new_address(self, obj):
        address_id = obj.get('address_id')
        if address_id:
            address = Address.objects.get(pk=address_id)
            if address:
                return AddressSerializer(address).data
        return None

    def to_representation(self, instance):
        """
        Customize the representation to include the absolute URL for the photo field if it exists.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if representation.get('new_photo') and request:
            representation['new_photo'] = request.build_absolute_uri(settings.MEDIA_URL + representation['new_photo'])
        
        if representation.get('new_address') is None:
            representation.pop('new_address', None)

        if representation.get('visa') is None:
            representation.pop('visa', None)
        return representation
    

class TaskUserSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    user_data = TaskUserDataSerializer()

    class Meta:
        model = Task
        fields = '__all__' 


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = '__all__' 
