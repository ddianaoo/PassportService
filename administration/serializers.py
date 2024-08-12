from rest_framework import serializers
from .models import Task
from authentication.serializers import UserListSerializer
from django.conf import settings


class UserDataSerializer(serializers.Serializer):
    photo = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
    surname = serializers.CharField(required=False, allow_blank=True)
    patronymic = serializers.CharField(required=False, allow_blank=True)
    address_id = serializers.IntegerField(required=False, allow_null=True)

    def to_representation(self, instance):
        """
        Customize the representation to include the absolute URL for the photo field if it exists.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if representation.get('photo') and request:
            representation['photo'] = request.build_absolute_uri(settings.MEDIA_URL + representation['photo'])
        
        if representation.get('address_id') is None:
            representation.pop('address_id', None)
        return representation
    

class TaskSerializer(serializers.ModelSerializer):
    user = UserListSerializer()
    user_data = UserDataSerializer()

    class Meta:
        model = Task
        fields = '__all__' 
