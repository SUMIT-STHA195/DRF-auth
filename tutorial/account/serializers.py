from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .utils import generate_otp, verify_otp


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username']


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password',
                  'confirm_password', 'first_name', 'last_name']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid Credential")
        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField()
    confirm_new_password = serializers.CharField()

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError(
                {"confirm_new_password": "passwords do not match"})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("old password doesnot match")
        return value

    def create(self, validated_data):
        email = self.context['request'].user.email
        user = User.objects.get(email=email)
        user.set_password(validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.CharField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with email doesnot exist")
        return value


class ResetPasswordVerifySerializer(serializers.Serializer):
    email = serializers.CharField()
    otp = serializers.CharField(max_length=6)
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if not verify_otp(data['otp'], data['email']):
            raise serializers.ValidationError("OTP doesnot match")
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("passwords do not match")
        return data

    def create(self, validated_data):
        email = validated_data['email']
        user = User.objects.get(email=email)
        user.set_password(validated_data['password'])
        user.save()
        return user
