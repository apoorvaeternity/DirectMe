from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from core.serializers import InventorySerializer
from .models import Profile


class UserProfileSerializer(serializers.ModelSerializer):
    # todo to be added
    # avatar = serializers.ReadOnlyField(source='profile.avatar', read_only=True)
    island = serializers.ReadOnlyField(source='profile.island.name', read_only=True)
    experience = serializers.ReadOnlyField(source='profile.experience', read_only=True)
    inventory = InventorySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'island', 'experience', 'inventory')
        read_only_fields = ('username', 'email', 'experience')


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        return Profile.objects.create_player(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email']
        )


class UserAuthenticationSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:

                if not user.is_active:
                    msg = 'User account is disabled.'
                    raise serializers.ValidationError(msg, code='authorization')

            else:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class UserGcmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('gcm_token',)


class UserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8)
