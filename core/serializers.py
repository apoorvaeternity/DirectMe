from rest_framework import serializers

from core.models import ShipStore, ShipUpgrade, Version


class ShipUpgradeDetailSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='item_id.name')

    class Meta:
        model = ShipUpgrade
        fields = ('item_id', 'name', 'count')


class ShipStoreSerializer(serializers.ModelSerializer):
    items_required = ShipUpgradeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = ShipStore
        fields = ('id', 'name', 'cost_multiplier', 'experience_gain', 'image', 'buy_cost', 'items_required')


class VersionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Version
        fields = '__all__'