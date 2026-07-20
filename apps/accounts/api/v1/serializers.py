from rest_framework import serializers

from apps.accounts.models import User
from common.constants import RoleChoices


class RegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    role = serializers.ChoiceField(
        choices=[RoleChoices.MASTER_AGENT, RoleChoices.MINOR_AGENT]
    )

    def validate_password(self, value):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError as DjangoValidationError

        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages) from None
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("A user with this phone already exists.")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "role",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "is_active", "date_joined"]


class CustomTokenObtainPairSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
