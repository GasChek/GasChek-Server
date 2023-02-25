from rest_framework import serializers
from accounts.models import Gaschek_Device
from .models import Gas_Leakage


class Gaschek_Device_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gaschek_Device
        fields = ['alarm', 'text', 'call', 'cylinder',
                  'gas_mass', 'gas_level', 'battery_level']


class Gaschek_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gaschek_Device
        fields = ['alarm', 'text', 'call']


class Gas_Leakage_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gas_Leakage
        fields = ['id', 'action', 'created_at']
