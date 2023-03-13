from rest_framework import serializers

class AdminLogInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()