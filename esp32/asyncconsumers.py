import json
from .serializers import Gaschek_Device_Serializer, Gaschek_Get_Serializer
from accounts.serializers import UserSerializer
from accounts.models import Gaschek_Device, User
from .models import Gas_Leakage
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models.signals import post_save
from functions.encryption import jwt_decoder
from asgiref.sync import sync_to_async
from django.dispatch import receiver


class GasDetailsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data):
        client_data = json.loads(text_data)

        if client_data["action"] == 'connect':
            @receiver(post_save, sender=Gaschek_Device, weak=False)
            async def send_data(**kwargs):
                try:
                    payload = jwt_decoder(client_data['gaschek'])
                    data = await sync_to_async(Gaschek_Device.objects.get)(user=payload['id'])
                    serializer = Gaschek_Device_Serializer(data)

                    await self.send(json.dumps({
                        'message': serializer.data
                    }))
                except Exception:
                    await self.send(json.dumps({
                        'message': 400
                    }))
            
            await send_data()

            # async def give_data(**kwargs):
            #     await send_data()

            # post_save.connect(give_data, sender=Gaschek_Device)

        if (client_data["action"] == 'alarm'):
            try:
                payload = jwt_decoder(client_data['gaschek'])
                data = await sync_to_async(Gaschek_Device.objects.get)(user=payload['id'])

                if (data.alarm == "on"):
                    data.alarm = "off"
                else:
                    data.alarm = "on"
                await sync_to_async(data.save)()

                # serializer = Gaschek_Device_Serializer(data)
                # await self.send(json.dumps({
                #     'message': serializer.data
                # }))
            except Exception:
                await self.send(json.dumps({
                    'message': 400
                }))            
          
        if (client_data["action"] == 'call'):
            try:
                payload = jwt_decoder(client_data['gaschek'])
                data = await sync_to_async(Gaschek_Device.objects.get)(user=payload['id'])

                if (data.call == "on"):
                    data.call = "off"
                else:
                    data.call = "on"
                await sync_to_async(data.save)()

                # serializer = Gaschek_Device_Serializer(data)
                # await self.send(json.dumps({
                #     'message': serializer.data
                # }))
            except Exception:
                await self.send(json.dumps({
                    'message': 400
                }))            
           
        if (client_data["action"] == 'text'):
            try:
                payload = jwt_decoder(client_data['gaschek'])
                data = await sync_to_async(Gaschek_Device.objects.get)(user=payload['id'])
                if (data.text == "on"):
                    data.text = "off"
                else:
                    data.text = "on"
                await sync_to_async(data.save)()

                # serializer = Gaschek_Device_Serializer(data)
                # await self.send(json.dumps({
                #     'message': serializer.data
                # }))
            except Exception:
                await self.send(json.dumps({
                    'message': 400
                }))            

class GasDetailsDeviceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()
        # pass

    async def receive(self, text_data):
        client_data = json.loads(text_data)

        if (client_data["action"] == 'connect'):
            async def send_data():
                user = User.objects.get(id=client_data['user_id'])
                data = Gaschek_Device.objects.get(user=user)
                serializer = Gaschek_Get_Serializer(data)
                serializer2 = UserSerializer(user)
                
                await self.send(json.dumps({
                    'call': serializer.data['call'],
                    'alarm': serializer.data['alarm'],
                    'text': serializer.data['text'], 
                    'country_code': serializer2.data['country_code'], 
                    'number_one': serializer2.data['phonenumber_ordering'],
                    'number_two': serializer2.data['phonenumber_gaschek_device_1'],
                    'number_three': serializer2.data['phonenumber_gaschek_device_2'],
                    'number_four': serializer2.data['phonenumber_gaschek_device_3']              
                }))
            send_data()

            async def give_data(**kwargs):
                send_data()

            post_save.connect(give_data, sender=Gaschek_Device)

class SendDeviceDetailsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()
        # pass

    async def receive(self, text_data):
        client_data = json.loads(text_data)

        user = User.objects.get(id=client_data['user_id'])
        gaschek_device = Gaschek_Device.objects.get(user=user)

        gaschek_device.cylinder = client_data['cylinder']
        gaschek_device.gas_mass = client_data['gas_mass']
        gaschek_device.gas_level = client_data['gas_level']
        gaschek_device.battery_level = client_data['battery_level']
        gaschek_device.save()

        # serializer = Gaschek_Get_Serializer(data)
        # serializer2 = UserSerializer(user)
        
        # self.send(json.dumps({
        #     'call': serializer.data['call'],
        #     'alarm': serializer.data['alarm'],
        #     'text': serializer.data['text'], 
        #     'country_code': serializer2.data['country_code'], 
        #     'number_one': serializer2.data['phonenumber_ordering'],
        #     'number_two': serializer2.data['phonenumber_gaschek_device_1'],
        #     'number_three': serializer2.data['phonenumber_gaschek_device_2'],
        #     'number_four': serializer2.data['phonenumber_gaschek_device_3']              
        # }))         

class GasLeakageNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()
        # pass

    async def receive(self, text_data):
        client_data = json.loads(text_data)

        if (client_data["action"] == 'connect'):
            async def send_data():
                try:
                    payload = jwt_decoder(client_data['gaschek'])
                    gaschek_device = Gaschek_Device.objects.get(user=payload['id'])
                    leak = Gas_Leakage.objects.filter(gaschek_device=gaschek_device)

                    await self.send(json.dumps({
                        'leakages': len(leak)
                    }))
                except Exception:
                    await self.send(json.dumps({
                        'leakages': 400
                    }))    

            async def give_data(**kwargs):
                send_data()

            post_save.connect(give_data, sender=Gas_Leakage)