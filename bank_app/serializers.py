from django.contrib.auth.models import User
from bank_app.models import BankOffer, BankApplication
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class BankOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankOffer
        fields = ["pk", "name", "description", "bonus", "fact", "cost", "imageUrl"]


class BankApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankApplication
        fields = ["pk", "status", "creation_date", "apply_date", "end_date", "psrn_and_company_name"]