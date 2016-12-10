from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from core.models import Item, Slot, ShipStore
from ship.models import Port, PortType, Dock, Ship
from .models import Profile, Token, Inventory


class UserProfileSerializer(serializers.ModelSerializer):
    experience = serializers.ReadOnlyField(source='profile.experience', read_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'experience')
        read_only_fields = ('username', 'email', 'experience')


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Initialize user data

        # Create profile
        profile = Profile(user=user)
        profile.save()

        # Create auth token
        token = Token(user=user)
        token.save()

        # Add inventory
        items = Item.objects.all()
        for item in items:
            inventory = Inventory(user=user, item=item, count=10)
            inventory.save()

        # Add ports(parking)
        for _ in range(2):
            port_type = PortType.objects.filter(name='Parking').first()
            parking_port = Port(user=user, type=port_type)
            parking_port.save()

        for _ in range(3):
            port_type = PortType.objects.filter(name='Non Parking').first()
            non_parking_port = Port(user=user, type=port_type)
            non_parking_port.save()

        # Adds docks(garage)
        for slot in Slot.objects.all():
            dock = Dock(user=user, slot=slot)
            dock.save()

        # Least Costly raft_from_store
        raft_from_store = ShipStore.objects.all().order_by('buy_cost').first()

        # Create ship for user
        raft = Ship(ship_store=raft_from_store, user=user)
        raft.save()

        # Dock requiring least level/experience
        dock = Dock.objects.filter(user=user).order_by('slot__unlock_level').first()

        # Give default raft to user
        dock.ship = raft
        dock.save()

        return user


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
