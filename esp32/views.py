from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import Gas_Leakage_Serializer, Gaschek_Get_Serializer
from accounts.serializers import UserSerializer
from accounts.models import Gaschek_Device
from accounts.models import User
from .models import Gas_Leakage
from functions.encryption import jwt_decoder, encrypt
from rest_framework.pagination import LimitOffsetPagination
from fcm_django.models import FCMDevice
from functions.notification import Notification
import json

from django.http import StreamingHttpResponse, JsonResponse
import asyncio
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from asgiref.sync import sync_to_async

    
######## UPDATE CYLINDER DETAILS COMING FROM DEVICE TO DATABASE
@method_decorator(csrf_exempt, name='dispatch')
class Update_esp32_details(View):
    async def post(self, request):
        try:
            payload = json.loads(request.body.decode('utf-8'))
            user = await sync_to_async(User.objects.get)(id=payload["user_id"])

            if not user:
                return Response({
                    "status": 400,
                    "message": "Invalid user"
                })

            if ('cylinder' not in payload and
                'gas_mass' not in payload and
                'gas_level' not in payload and
                'battery_level' not in payload and 
                'indicator' not in payload):
                return JsonResponse({
                    "status": 400,
                })
                
            gaschek_device = await sync_to_async(Gaschek_Device.objects.get)(user=user)
            
            gaschek_device.cylinder = payload['cylinder']
            gaschek_device.gas_mass = payload['gas_mass']
            gaschek_device.gas_level = payload['gas_level']
            gaschek_device.battery_level = payload['battery_level']
            gaschek_device.indicator = payload['indicator']
            await sync_to_async(gaschek_device.save)()

            return JsonResponse({
                'status': 200,
            })
        except Exception as e:
            print(e)

######## GET CYLINDER DETAILS COMING FROM DATABASE TO DEVICE
@method_decorator(gzip_page, name='dispatch')
class Get_gaschek_details(APIView):
    def get(self, request):
        user = User.objects.get(id=request.query_params['user_id'])
        gaschek_device = Gaschek_Device.objects.filter(user=user).first()

        if not gaschek_device:
            return Response({
                'status': 400
            })

        serializer = Gaschek_Get_Serializer(gaschek_device)
        serializer2 = UserSerializer(user)

        return Response({
            'call': serializer.data['call'],
            'alarm': serializer.data['alarm'],
            'text': serializer.data['text'],
            'indicator': serializer.data['indicator'],
            'country_code': serializer2.data['country_code'],
            'number_one': serializer2.data['phonenumber_ordering'],
            'number_two': serializer2.data['phonenumber_gaschek_device_1'],
            'number_three': serializer2.data['phonenumber_gaschek_device_2'],
            'number_four': serializer2.data['phonenumber_gaschek_device_3']
        })

@method_decorator(gzip_page, name='dispatch')
class Report_gas_leakage(APIView, LimitOffsetPagination):
    def post(self, request):
        user = User.objects.get(id=request.data['user_id'])

        if not user:
            return Response({
                "status": 400,
                "message": "Invalid user"
            })

        gaschek_device = Gaschek_Device.objects.get(user=user)
        Gas_Leakage.objects.create(gaschek_device=gaschek_device, action=request.data['action'])
        fcm = FCMDevice.objects.filter(user_id=user.id)

        try:
            if request.data['action'] == "smoke":
                if fcm:
                    for device in fcm:
                        Notification(
                            reg_id=device.registration_id,
                            title="GasChek alert",
                            body="GasChek detected smoke",
                        ).start()
                    # notificaton
                return Response({
                    'status': 200
                })
            else:
                if fcm:
                    for device in fcm:
                        Notification(
                            reg_id=device.registration_id,
                            title="GasChek alert",
                            body="GasChek detected gas leakage",
                        ).start()
                    # notificaton
                return Response({
                    'status': 200
                })
        except Exception as e:
            print(e)


    def get(self, request):
        try:
            payload = jwt_decoder(request.META.get('HTTP_AUTHORIZATION'))
            user = User.objects.get(id=payload['id'])

            if not user:
                return Response({
                    "status": 400,
                    "message": "Invalid user"
                })

            gaschek_device = Gaschek_Device.objects.get(user=user)
            gas_leakage = Gas_Leakage.objects.filter(
                gaschek_device=gaschek_device).order_by('created_at').reverse()


            results = self.paginate_queryset(gas_leakage, request, view=self)
            serializer = Gas_Leakage_Serializer(results, many=True)
            return self.get_paginated_response(encrypt(json.dumps(serializer.data)))
        
        except Exception:
            return Response({
                "status": 400,
            })


async def stream(payload):
    while True:
        user = await sync_to_async(User.objects.get)(id=payload['user_id'])
        gaschek_device = await sync_to_async(Gaschek_Device.objects.filter)(user=user)
        gaschek_device = await sync_to_async(gaschek_device.first)()

        data = None
        if not gaschek_device:
            data = {
                'status': 400
            }
            yield data
            break
        
        serializer = await sync_to_async(Gaschek_Get_Serializer)(gaschek_device)
        serializer2 = await sync_to_async(UserSerializer)(user)

        await asyncio.sleep(0.5)
        data = {
            'call': serializer.data['call'],
            'alarm': serializer.data['alarm'],
            'text': serializer.data['text'],
            'indicator': serializer.data['indicator'],
            'country_code': serializer2.data['country_code'],
            'number_one': serializer2.data['phonenumber_ordering'],
            'number_two': serializer2.data['phonenumber_gaschek_device_1'],
            'number_three': serializer2.data['phonenumber_gaschek_device_2'],
            'number_four': serializer2.data['phonenumber_gaschek_device_3']
        }
        yield json.dumps(data)

@method_decorator(csrf_exempt, name='dispatch')
class Get_gaschek_details_SSE(View):
    async def post(self, request):
        payload = json.loads(request.body.decode('utf-8'))

        return StreamingHttpResponse(
            streaming_content=stream(payload),
            content_type="text/event-stream"
        )

