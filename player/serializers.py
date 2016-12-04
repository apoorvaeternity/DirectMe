from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer

from .models import Profile, Token


class UserRegistrationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        profile = Profile(user=user)
        profile.save()

        token = Token(user=user)
        token.save()

        return user


class UserAuthenticationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
