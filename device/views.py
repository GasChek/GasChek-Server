from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import Leakage_History_Serializer, LogInSerializer
from accounts.models import User
from .models import Leakage_History, Gaschek_Device
from functions.encryption import auth_decoder, encrypt, auth_encoder
from functions.CustomQuery import get_if_exists
from rest_framework.pagination import LimitOffsetPagination
from fcm_django.models import FCMDevice
from functions.notification import Notification
import json
import datetime

# from django.http import StreamingHttpResponse, JsonResponse
# import asyncio
# from django.views.generic import View
# from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page

# from asgiref.sync import sync_to_async


@method_decorator(gzip_page, name="dispatch")
class ConnectDeviceAPI(APIView):
    def error_res(self):
        return Response({"status": 400, "message": "Invaild device id or password"})

    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            serializer = LogInSerializer(data=request.data)

            if serializer.is_valid():
                device_id = serializer.data["device_id"]
                password = serializer.data["password"]

                device = get_if_exists(Gaschek_Device, device_id=device_id)

                if (
                    not device
                    or device.password != password
                    or device.is_connected_with_device is False
                ):
                    return self.error_res()

                user = get_if_exists(User, id=payload["id"])
                device.user = user
                device.save()

                payload = {
                    "device_id": device.device_id,
                    "account_type": "user",
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
                    "iat": datetime.datetime.utcnow(),
                }
                token = auth_encoder(payload)
                return Response(
                    {
                        "status": 200,
                        "message": "Connected",
                        "token": token,
                    }
                )
            else:
                return self.error_res()
        except Exception:
            return Response(
                {"status": 400, "message": "Something went wrong, try again later"}
            )


@method_decorator(gzip_page, name="dispatch")
class Report_leakage(APIView, LimitOffsetPagination):
    def post(self, request):
        device = Gaschek_Device.objects.get(device_id=request.data["device_id"])

        if not device:
            return Response({"status": 400, "message": "Invalid device"})

        Leakage_History.objects.create(device=device, action=request.data["action"])
        fcm = FCMDevice.objects.filter(user_id=device.user.id)

        try:
            if request.data["action"] == "smoke":
                if fcm:
                    for device in fcm:
                        Notification(
                            reg_id=device.registration_id,
                            title="GasChek alert",
                            body="GasChek detected smoke",
                        ).start()
                    # notificaton
                return Response({"status": 200})
            else:
                if fcm:
                    for device in fcm:
                        Notification(
                            reg_id=device.registration_id,
                            title="GasChek alert",
                            body="GasChek detected gas leakage",
                        ).start()
                    # notificaton
                return Response({"status": 200})
        except Exception as e:
            print(e)

    def get(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            device = Gaschek_Device.objects.get(device_id=payload["device_id"])

            if not device:
                return Response({"status": 400, "message": "Invalid device"})

            leakages = Leakage_History.objects.filter(device=device).order_by(
                "-created_at"
            )

            results = self.paginate_queryset(leakages, request, view=self)
            serializer = Leakage_History_Serializer(results, many=True)
            return self.get_paginated_response(encrypt(json.dumps(serializer.data)))

        except Exception:
            return Response(
                {
                    "status": 400,
                }
            )


######## UPDATE CYLINDER DETAILS COMING FROM DEVICE TO DATABASE
# @method_decorator(csrf_exempt, name='dispatch')
# class Update_device_details(View):
#     async def post(self, request):
#         try:
#             payload = json.loads(request.body.decode('utf-8'))
#             user = await sync_to_async(User.objects.get)(id=payload["user_id"])

#             if not user:
#                 return Response({
#                     "status": 400,
#                     "message": "Invalid user"
#                 })

#             if ('cylinder' not in payload and
#                 'gas_mass' not in payload and
#                 'gas_level' not in payload and
#                 'battery_level' not in payload and
#                 'indicator' not in payload):
#                 return JsonResponse({
#                     "status": 400,
#                 })

#             gaschek_device = await sync_to_async(Gaschek_Device.objects.get)(user=user)

#             gaschek_device.cylinder = payload['cylinder']
#             gaschek_device.gas_mass = payload['gas_mass']
#             gaschek_device.gas_level = payload['gas_level']
#             gaschek_device.battery_level = payload['battery_level']
#             gaschek_device.indicator = payload['indicator']
#             await sync_to_async(gaschek_device.save)()

#             return JsonResponse({
#                 'status': 200,
#             })
#         except Exception as e:
#             print(e)

# async def stream(payload):
#     while True:
#         user = await sync_to_async(User.objects.get)(id=payload['user_id'])
#         gaschek_device = await sync_to_async(Gaschek_Device.objects.filter)(user=user)
#         gaschek_device = await sync_to_async(gaschek_device.first)()

#         data = None
#         if not gaschek_device:
#             data = {
#                 'status': 400
#             }
#             yield data
#             break

#         # serializer = await sync_to_async(Gaschek_Get_Serializer)(gaschek_device)
#         # serializer2 = await sync_to_async(UserSerializer)(user)

#         await asyncio.sleep(0.5)
#         data = {
#             'call': gaschek_device.call,
#             'alarm': gaschek_device.alarm,
#             'text': gaschek_device.text,
#             'indicator': gaschek_device.indicator,
#             'country_code': user.country_code,
#             'number_one': user.phonenumber_ordering,
#             'number_two': user.phonenumber_gaschek_device_1,
#             'number_three': user.phonenumber_gaschek_device_2,
#             'number_four': user.phonenumber_gaschek_device_3
#         }
#         yield json.dumps(data)

# @method_decorator(csrf_exempt, name='dispatch')
# class Get_gaschek_details_SSE(View):
#     async def post(self, request):
#         payload = json.loads(request.body.decode('utf-8'))

#         return StreamingHttpResponse(
#             streaming_content=stream(payload),
#             content_type="text/event-stream"
#         )
