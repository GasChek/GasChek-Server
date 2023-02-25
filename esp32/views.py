from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (Gaschek_Get_Serializer,
                          Gas_Leakage_Serializer,)
from accounts.serializers import UserSerializer
from accounts.models import Gaschek_Device
from accounts.models import User
from .models import Gas_Leakage
from functions.encryption import jwt_decoder

# Create your views here.


class Update_esp32_details(APIView):
    def post(self, request):
        try:
            user = User.objects.get(id=request.data["user_id"])

            if not user:
                return Response({
                    "status": 400,
                    "message": "Invalid user"
                })

            if ('cylinder' not in request.data and
                'gas_mass' not in request.data and
                'gas_level' not in request.data and
                'battery_level' not in request.data):
                return Response({
                    "status": 400,
                })
                
            gaschek_device = Gaschek_Device.objects.get(user=user)

            gaschek_device.cylinder = request.data.get(
                'cylinder', gaschek_device.cylinder)
            gaschek_device.gas_mass = request.data.get(
                'gas_mass', gaschek_device.gas_mass)
            gaschek_device.gas_level = request.data.get(
                'gas_level', gaschek_device.gas_level)
            gaschek_device.battery_level = request.data.get(
                'battery_level', gaschek_device.battery_level)
            gaschek_device.save()

            return Response({
                'status': 200,
            })
        except Exception as e:
            print(e)


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
            'country_code': serializer2.data['country_code'],
            'number_one': serializer2.data['phonenumber_ordering'],
            'number_two': serializer2.data['phonenumber_gaschek_device_1'],
            'number_three': serializer2.data['phonenumber_gaschek_device_2'],
            'number_four': serializer2.data['phonenumber_gaschek_device_3']
        })


class Report_gas_leakage(APIView):
    def post(self, request):
        user = User.objects.get(id=request.data['user_id'])

        if not user:
            return Response({
                "status": 400,
                "message": "Invalid user"
            })

        gaschek_device = Gaschek_Device.objects.get(user=user)
        Gas_Leakage.objects.create(gaschek_device=gaschek_device, action=request.data['action'])

        return Response({
            'status': 200
        })

    def get(self, request):
        payload = jwt_decoder(request.query_params['token'])
        user = User.objects.get(id=payload['id'])

        if not user:
            return Response({
                "status": 400,
                "message": "Invalid user"
            })

        gaschek_device = Gaschek_Device.objects.get(user=user)
        gas_leakage = Gas_Leakage.objects.filter(
            gaschek_device=gaschek_device).order_by('created_at').reverse()

        serialzer = Gas_Leakage_Serializer(gas_leakage, many=True)

        return Response({
            'status': 200,
            'data': serialzer.data
        })


class Get_Leakage_Notification_Details(APIView):
    def get(self, request):
        try:
            payload = jwt_decoder(request.query_params['gaschek'])
            gaschek_device = Gaschek_Device.objects.get(user=payload['id'])
            leak = Gas_Leakage.objects.filter(gaschek_device=gaschek_device)

            return Response({
                'status': 200,
                'data': len(leak)
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'Unauthenticated'
            })


# class Reset_GasChek_device(APIView):
#     def post(self, request):
#         payload = jwt_decoder(request.data['token'])
#         user = User.objects.get(id=payload['id'])

#         if not user:
#             return Response({
#                 "status": 400,
#                 "message": "Invalid user"
#             })

#         gaschek_device = Gaschek_Device.objects.get(user=user)
#         gaschek_device.gas_level = 0
#         gaschek_device.gas_mass = 0
#         gaschek_device.cylinder = '0kg'
#         gaschek_device.save()

#         serializer = Gaschek_Device_Serializer(gaschek_device)

#         return Response({
#             'status': 200,
#             'data': serializer.data
#         })
