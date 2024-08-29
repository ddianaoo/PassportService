from rest_framework import serializers
from authentication.models import CustomUser
from .models import Address, Passport, ForeignPassport


class CreateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country_code', 'region', 'settlement', 'street', 'apartments', 'post_code']


class RetrieveAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country_code', 'region', 'settlement', 'street', 'apartments', 'post_code']


class PhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()


class RetrieveInternalPassportSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    
    name = serializers.CharField(source='user.name')
    surname = serializers.CharField(source='user.surname')
    patronymic = serializers.CharField(source='user.patronymic')
    sex = serializers.CharField(source='user.sex')
    date_of_birth = serializers.DateField(source='user.date_of_birth')
    place_of_birth = serializers.CharField(source='user.place_of_birth')
    nationality = serializers.CharField(source='user.get_nationality_display')
    record_number = serializers.CharField(source='user.record_number')

    registration_address = RetrieveAddressSerializer(source='user.address')

    class Meta:
        model = Passport
        fields = ('number', 'authority', 'date_of_issue', 'date_of_expiry', 
            'photo', 'name', 'surname', 'patronymic', 'sex', 'date_of_birth', 
            'record_number', 'place_of_birth', 'nationality', 'registration_address')
        
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


class RetrieveForeignPassportSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    name = serializers.CharField(source='user.name')
    surname = serializers.CharField(source='user.surname')
    patronymic = serializers.CharField(source='user.patronymic')
    sex = serializers.CharField(source='user.sex')
    date_of_birth = serializers.DateField(source='user.date_of_birth')
    place_of_birth = serializers.CharField(source='user.place_of_birth')
    nationality = serializers.CharField(source='user.get_nationality_display')
    record_number = serializers.CharField(source='user.record_number')
    country_code = serializers.CharField(source='user.nationality')

    class Meta:
        model = ForeignPassport
        fields = ('number', 'authority', 'date_of_issue', 'date_of_expiry', 
            'photo', 'name', 'surname', 'patronymic', 'sex', 'date_of_birth', 
            'record_number', 'place_of_birth', 'nationality', 'country_code')
        
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


class RetrieveDocumentsSerializer(serializers.ModelSerializer):
    internal_passport = RetrieveInternalPassportSerializer(source='passport')
    foreign_passport = RetrieveForeignPassportSerializer()

    class Meta:
        model = CustomUser
        fields = ('internal_passport', 'foreign_passport', )


class CreateInternalPassportSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(required=False)
    photo = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Passport
        fields = ('number', 'authority', 'date_of_issue', 'date_of_expiry', 
            'photo', )
        
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None
    

class CreateForeignPassportSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(required=False)
    photo = serializers.SerializerMethodField(required=False)
    
    class Meta:
        model = ForeignPassport
        fields = ('number', 'authority', 'date_of_issue', 'date_of_expiry', 
            'photo', )
        
    def get_photo(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None


class RestorePassportSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=[('loss', 'Loss'), ('expiry', 'Expiry')])
    photo = serializers.ImageField()
