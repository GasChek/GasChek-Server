import json
from .serializers import Gaschek_Device_Serializer, Gaschek_Get_Serializer
from accounts.serializers import UserSerializer
from accounts.models import Gaschek_Device, User
from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from django.db.models.signals import post_save
from functions.encryption import jwt_decoder, encrypt, decrypt
from asgiref.sync import sync_to_async


class GasDetailsConsumer(WebsocketConsumer):
    def connect(self):
        token = self.scope['query_string'].decode('utf-8')
        try:
            payload = jwt_decoder(token)
            self.token_id = payload['id']
            self.accept()
        except Exception:
            self.close()

    def disconnect(self, close_code):
        self.close()

    def receive(self, bytes_data):
        try:
            convert_byte_to_text = bytes_data.decode('utf-8')
            decrypted_text_data = decrypt(convert_byte_to_text)
            client_data = json.loads(decrypted_text_data)

            if client_data["action"] == 'cnt':
                def send_data():
                    data = Gaschek_Device.objects.get(user=self.token_id)
                    serializer = Gaschek_Device_Serializer(data)
                    encrypted_data = encrypt(json.dumps(serializer.data))

                    data = encrypt(json.dumps({
                        'msg': encrypted_data
                    })).encode('utf-8')
                    self.send(bytes_data=data)

                send_data()

                def give_data(instance, **kwargs):
                    if (instance.user.id == self.token_id):
                        send_data()
                post_save.connect(give_data, sender=Gaschek_Device, weak=False)
        except Exception:
            self.send(bytes_data=encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8'))


class ToggleDetailsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        token = self.scope['query_string'].decode('utf-8')
        try:
            payload = jwt_decoder(token)
            self.token_id = payload['id']
            await self.accept()
        except Exception:
            await self.close()

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, bytes_data):
        try:
            convert_byte_to_text = bytes_data.decode('utf-8')
            decrypted_text_data = decrypt(convert_byte_to_text)
            client_data = json.loads(decrypted_text_data)

            if client_data["action"] == 'cnt':
                data = encrypt(json.dumps({
                    'msg': 200
                })).encode('utf-8')
                await self.send(bytes_data=data)

            data2 = encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8')

            data = await sync_to_async(Gaschek_Device.objects.get)(user=self.token_id)
            if (client_data["action"] == 'a'):
                try:
                    if (data.alarm == "on"):
                        data.alarm = "off"
                    else:
                        data.alarm = "on"
                    await sync_to_async(data.save)()

                except Exception:
                    await self.send(bytes_data=data2)

            if (client_data["action"] == 'c'):
                try:
                    if (data.call == "on"):
                        data.call = "off"
                    else:
                        data.call = "on"
                    await sync_to_async(data.save)()

                except Exception:
                    self.send(bytes_data=data2)

            if (client_data["action"] == 't'):
                try:
                    if (data.text == "on"):
                        data.text = "off"
                    else:
                        data.text = "on"
                    await sync_to_async(data.save)()
                except Exception:
                    await self.send(bytes_data=data2)

            if (client_data["action"] == 'i'):
                try:
                    if (data.indicator == "on"):
                        data.indicator = "off"
                    else:
                        data.indicator = "on"
                    await sync_to_async(data.save)()

                except Exception:
                    await self.send(bytes_data=data2)

        except Exception:
            data2 = encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8')
            await self.send(bytes_data=data2)


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

            def give_data(instance, **kwargs):
                if (instance.user.id == client_data['user_id']):
                    send_data()
            post_save.connect(give_data, sender=Gaschek_Device, weak=False)

            try:
                data = Gaschek_Device.objects.get(user=self.token_id)
                if (data.indicator == "on"):
                    data.indicator = "off"
                else:
                    data.indicator = "on"
                data.save()

            except Exception:
                self.send(json.dumps({
                    'msg': 400
                }))


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
