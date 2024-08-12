from rest_framework import serializers
from .models import Address, Passport, ForeignPassport


class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country_code', 'region', 'settlement', 'street', 'apartments', 'post_code']


class AddressRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country_code', 'region', 'settlement', 'street', 'apartments', 'post_code']


class PhotoSerializer(serializers.Serializer):
    photo = serializers.ImageField()


class PassportRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passport
        fields = "__all__"


class ForeignPassportRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForeignPassport
        fields = "__all__"
