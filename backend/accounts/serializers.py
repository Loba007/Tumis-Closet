from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Address

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Normalize the email before authentication so logins are case-insensitive."""

    def validate(self, attrs):
        email = attrs.get("email")
        if isinstance(email, str):
            attrs["email"] = email.strip().lower()
        return super().validate(attrs)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "phone_number", "password"]

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return email

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.email_verified = False
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "email", "email_verified", "username", "first_name",
            "last_name", "phone_number", "created_at",
        ]
        read_only_fields = ["id", "email", "email_verified", "created_at"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id", "full_name", "phone_number", "line1", "line2",
            "city", "state", "country", "is_default", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data):
        user = self.context["request"].user
        if validated_data.get("is_default"):
            Address.objects.filter(user=user).update(is_default=False)
        return Address.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        if validated_data.get("is_default"):
            Address.objects.filter(user=instance.user).exclude(pk=instance.pk).update(
                is_default=False
            )
        return super().update(instance, validated_data)
