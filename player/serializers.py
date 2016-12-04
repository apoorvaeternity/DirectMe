from django.contrib.auth.models import User
from rest_framework.serializers import ModelSerializer


class UserRegistrationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )


class UserAuthenticationSeriaizer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password')
