from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate


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

    def check_old_password(pass1, pass2):
        if pass1 == pass2:
            return True

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("passwords do not match")
        else:
            user = self.context['request'].user
            if not user.check_password(data['old_password']):
                raise serializers.ValidationError("old password doesnot match")
            return {
                "user": user,
                "new_password": data['new_password']
            }

    def create(self, validated_data):
        user = User.objects.get(email=validated_data["user"].email)
        user.set_password(validated_data['new_password'])
        user.save()
        return user
