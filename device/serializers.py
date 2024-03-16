from rest_framework import serializers
from .models import Leakage_History, Gaschek_Device

class Gaschek_Device_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gaschek_Device
        fields = ['device_id', 'alarm', 'text', 'call', 'cylinder', 'indicator',
                  'gas_mass', 'gas_level', 'battery_level', 'device_update_time',
                  'country_code','phonenumber_one', 'phonenumber_two', 'phonenumber_three']

class Gaschek_Get_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gaschek_Device
        fields = ['alarm', 'text', 'call', 'indicator']

class Leakage_History_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Leakage_History
        fields = ['id', 'action', 'created_at']

class LogInSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    password = serializers.CharField()