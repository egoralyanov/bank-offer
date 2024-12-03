from django.contrib.auth.models import User
from bank_app.models import BankOffer, BankApplication
from collections import OrderedDict
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "is_staff", "is_superuser"]


class BankOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankOffer
        fields = ["pk", "name", "description", "bonus", "fact", "cost", "imageUrl"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields 


class BankApplicationSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(source='user.username', read_only=True)
    moderator = serializers.SerializerMethodField()

    class Meta:
        model = BankApplication
        fields = ["pk", "status", "creation_date", "apply_date", "end_date", "creator", "moderator", "psrn_and_company_name"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False
                new_fields[name] = field
            return new_fields

    def get_moderator(self, obj):
        return obj.moderator.email if obj.moderator else None
