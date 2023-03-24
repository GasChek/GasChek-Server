import json, os, random
from .serializers import Gaschek_Device_Serializer, Gaschek_Get_Serializer
from accounts.serializers import UserSerializer
from accounts.models import Gaschek_Device, User
from .models import Gas_Leakage
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.db.models.signals import post_save
from functions.encryption import jwt_decoder, encrypt
from asgiref.sync import sync_to_async
from dotenv import load_dotenv

load_dotenv()
JWT_KEY = os.getenv('JWT_KEY')

class GasDetailsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close()

    def receive(self, text_data):
        client_data = json.loads(text_data)

        if client_data["action"] == 'cnt':
            def send_data():
                try:
                    payload = jwt_decoder(client_data['gaschek'])
                    data = Gaschek_Device.objects.get(user=payload['id'])
                    serializer = Gaschek_Device_Serializer(data)
                    encrypted_data = encrypt(json.dumps(serializer.data))
        
                    self.send(json.dumps({
                        'msg':encrypted_data
                    }))  
                        
                except Exception:
                    self.send(json.dumps({
                        'msg':400
                    }))
            send_data()

            def give_data(**kwargs):
                send_data()
            post_save.connect(give_data, sender=Gaschek_Device, weak=False)        

class ToggleGasDetailsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data):
        client_data = json.loads(text_data)

        if (client_data["action"] == 'a'):
            try:
                payload = jwt_decoder(client_data['gaschek'])
                data = await sync_to_async(Gaschek_Device.objects.get)(user=payload['id'])

                if (data.alarm == "on"):
                    data.alarm = "off"
                else:
                    data.alarm = "on"
                await sync_to_async(data.save)()

            except Exception:
                await self.send(json.dumps({
                    'message': 400
                }))            
          
        if (client_data["action"] == 'c'):
            try:
                payload = jwt_decoder(client_data['gaschek'])
                data = await sync_to_async(Gaschek_Device.objects.get)(user=payload['id'])

                if (data.call == "on"):
                    data.call = "off"
                else:
                    data.call = "on"
                await sync_to_async(data.save)()

            except Exception:
                await self.send(json.dumps({
                    'msg': 400
                }))            
           
        if (client_data["action"] == 't'):
            try:
                payload = jwt_decoder(client_data['gaschek'])
                data = await sync_to_async(Gaschek_Device.objects.get)(user=payload['id'])
                if (data.text == "on"):
                    data.text = "off"
                else:
                    data.text = "on"
                await sync_to_async(data.save)()

            except Exception:
                await self.send(json.dumps({
                    'msg': 400
                }))            

class GasDetailsDeviceConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close()
        # pass

    def receive(self, text_data):
        client_data = json.loads(text_data)

        if (client_data["action"] == 'connect'):
            def send_data():
                user = User.objects.get(id=client_data['user_id'])
                data = Gaschek_Device.objects.get(user=user)
                serializer = Gaschek_Get_Serializer(data)
                serializer2 = UserSerializer(user)
                
                self.send(json.dumps({
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

            def give_data(**kwargs):
                send_data()

            post_save.connect(give_data, sender=Gaschek_Device, weak=False)

class SendDeviceDetailsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()
        # pass

    async def receive(self, text_data):
        client_data = json.loads(text_data)

        user = await sync_to_async(User.objects.get)(id=client_data['user_id'])
        gaschek_device = await sync_to_async(Gaschek_Device.objects.get)(user=user)

        gaschek_device.cylinder = client_data['cylinder']
        gaschek_device.gas_mass = client_data['gas_mass']
        gaschek_device.gas_level = client_data['gas_level']
        gaschek_device.battery_level = client_data['battery_level']
        await sync_to_async(gaschek_device.save)()

class GasLeakageNotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close()
        # pass

    def receive(self, text_data):
        client_data = json.loads(text_data)

        if (client_data["action"] == 'cnt'):
            def send_data():
                try:
                    payload = jwt_decoder(client_data['gaschek'])
                    gaschek_device = Gaschek_Device.objects.get(user=payload['id'])
                    leak = Gas_Leakage.objects.filter(gaschek_device=gaschek_device)

                    self.send(json.dumps({
                        'status': 200,
                        'leakages': len(leak)
                    }))
                except Exception:
                    self.send(json.dumps({
                        'status': 400,
                    }))   

            send_data() 

            def give_data(**kwargs):
                send_data()

            post_save.connect(give_data, sender=Gas_Leakage, weak=False)