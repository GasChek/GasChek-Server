from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import Leakage_History_Serializer, LogInSerializer
from accounts.models import User
from .models import Leakage_History, Gaschek_Device
from accounts.utils.auth_utils import generate_auth_token, jwt_required
from functions.encryption import encrypt
from functions.CustomQuery import get_if_exists
from rest_framework.pagination import LimitOffsetPagination
from fcm_django.models import FCMDevice
from functions.notification import Notification
import json
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page


@method_decorator(gzip_page, name="dispatch")
class ConnectDeviceAPI(APIView):
    def error_res(self):
        return Response(
            {"msg": "Invaild device id or password"}, status=status.HTTP_400_BAD_REQUEST
        )

    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            serializer = LogInSerializer(data=request.data)

            if not serializer.is_valid():
                return self.error_res()
            device_id = serializer.data["device_id"]
            password = serializer.data["password"]

            device = get_if_exists(Gaschek_Device, device_id=device_id)

            if (
                not device
                or device.password != password
                or device.is_connected_with_device is False
            ):
                return self.error_res()

            user = get_if_exists(User, id=request.payload["id"])
            device.user = user
            device.save()
            token = generate_auth_token(user, "device", "user", device.device_id)
            return Response(
                {
                    "token": token,
                }
            )

        except Exception as e:
            print(e)
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class Report_leakage(APIView, LimitOffsetPagination):
    def post(self, request):
        try:
            device = Gaschek_Device.objects.get(device_id=request.data["device_id"])
            if not device:
                return Response(
                    {"msg": "Invalid device"}, status=status.HTTP_400_BAD_REQUEST
                )

            Leakage_History.objects.create(device=device, action=request.data["action"])
            fcm = FCMDevice.objects.filter(user_id=device.user.id)

            if request.data["action"] == "smoke":
                for device in fcm:
                    Notification(
                        reg_id=device.registration_id,
                        title="GasChek alert",
                        body="GasChek detected smoke",
                    ).start()
                return Response({"msg": "ok"})
            for device in fcm:
                Notification(
                    reg_id=device.registration_id,
                    title="GasChek alert",
                    body="GasChek detected gas leakage",
                ).start()
            return Response({"msg": "ok"})
        except Exception as e:
            print(e)
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @method_decorator(jwt_required(token_type="device"))
    def get(self, request):
        try:
            device = Gaschek_Device.objects.get(device_id=request.payload["device_id"])

            if not device:
                return Response(
                    {"msg": "Invalid device"}, status=status.HTTP_400_BAD_REQUEST
                )

            leakages = Leakage_History.objects.filter(device=device).order_by(
                "-created_at"
            )

            results = self.paginate_queryset(leakages, request, view=self)
            serializer = Leakage_History_Serializer(results, many=True)
            return self.get_paginated_response(encrypt(json.dumps(serializer.data)))

        except Exception as e:
            print(e)
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
