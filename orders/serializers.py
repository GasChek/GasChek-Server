from rest_framework import serializers
from .models import Gas_orders
from accounts.models import Cylinder_Price


class Cylinder_Price_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Cylinder_Price
        fields = ["id", "cylinder", "price"]


class Order_Serializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    address = serializers.CharField(source="user.address")
    company_name = serializers.CharField(source="gas_dealer.company_name")
    phonenumber = serializers.CharField(source="gas_dealer.phonenumber")

    class Meta:
        model = Gas_orders
        fields = [
            "id",
            "cylinder",
            "price",
            "delivery",
            "first_name",
            "last_name",
            "address",
            "phonenumber",
            "company_name",
            "created_at",
            "dealer_confirmed",
            "user_confirmed",
        ]


class Delivery_Fee_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Gas_orders
        fields = ["id", "price"]
