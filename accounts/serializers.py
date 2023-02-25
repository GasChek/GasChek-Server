from rest_framework import serializers
from .models import User, Gas_Dealer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', "usernames", "firstname",
                  "lastname", "is_active", "password",
                  "is_dealer", "is_verified", "country_code",
                  "phonenumber_ordering",
                  "phonenumber_gaschek_device_1",
                  "phonenumber_gaschek_device_2",
                  "phonenumber_gaschek_device_3",
                  "address", 'state']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class GasDealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gas_Dealer
        fields = ['id', 'user', 'company_name',
                  'location', 'selling', 'open', 'state']


class GasDealerSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gas_Dealer
        fields = ['id', 'company_name', 'open']


class LogInSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class DealerLogInSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()
