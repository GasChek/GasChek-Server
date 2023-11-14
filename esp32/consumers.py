import json
from .serializers import Gaschek_Device_Serializer
from accounts.models import Gaschek_Device, User
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save
from functions.encryption import jwt_decoder, encrypt, decrypt
# MQTT
import paho.mqtt.client as paho
from paho import mqtt
from dotenv import load_dotenv
import os
import random
import string
load_dotenv()
# MQTT


def generate_random_text(length=10):
    characters = string.ascii_letters + string.digits
    random_text = ''.join(random.choice(characters) for i in range(length))
    return random_text
        
def connect_to_mqtt_broker(topic):
    client = paho.Client(client_id=f'mqtt-GasChek-client-{generate_random_text()}', userdata=None, protocol=paho.MQTTv5)
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(str(os.getenv('MQTT_USER')), str(os.getenv('MQTT_PASSWORD')))
    client.connect(str(os.getenv('MQTT_SERVER_URL')), int(os.getenv('MQTT_PORT')))
    client.subscribe(str(topic), qos=1)
    return client

class GasDetailsConsumer(WebsocketConsumer):
    def connect(self):
        token = self.scope['query_string'].decode('utf-8')
        try:
            payload = jwt_decoder(token)
            self.token_id = payload['id']
            self.client = connect_to_mqtt_broker(self.token_id)
            self.accept()
        except Exception:
            self.close()

    def disconnect(self, close_code):
        self.client.unsubscribe(str(self.token_id))
        self.client.loop_stop()
        self.close()

    def receive(self, bytes_data):
        try:
            convert_byte_to_text = bytes_data.decode('utf-8')
            decrypted_text_data = decrypt(convert_byte_to_text)
            client_data = json.loads(decrypted_text_data)

            def get_device():
                data = Gaschek_Device.objects.get(user=self.token_id)
                return data

            def send_data():
                serializer = Gaschek_Device_Serializer(get_device())
                encrypted_data = encrypt(json.dumps(serializer.data))

                data = encrypt(json.dumps({
                    'msg': encrypted_data
                })).encode('utf-8')
                self.send(bytes_data=data)

            def publish_data_to_mqtt():
                user = User.objects.get(id=self.token_id)
                gaschek_device = get_device()

                payload = json.dumps({
                    'alarm': gaschek_device.alarm,
                    'call': gaschek_device.call,
                    'text': gaschek_device.text,
                    'indicator': gaschek_device.indicator,
                    'country_code': user.country_code,
                    'number_one': user.phonenumber_ordering,
                    'number_two': user.phonenumber_gaschek_device_1,
                    'number_three': user.phonenumber_gaschek_device_2,
                    'number_four': user.phonenumber_gaschek_device_3
                })
                self.client.publish(str(self.token_id), payload=payload, qos=0)
  
            def receive_data_from_mqtt():
                def on_message(client, userdata, msg):
                    device_data = json.loads(msg.payload.decode('utf-8'))
                    if "cylinder" in device_data:
                        device = get_device()
                        device.cylinder = device_data["cylinder"]
                        device.gas_mass = device_data["gas_mass"]
                        device.gas_level = device_data["gas_level"]
                        device.battery_level = device_data["battery_level"]
                        device.indicator = device_data["indicator"]
                        device.save()
                self.client.on_message = on_message
                self.client.loop_start()

            if client_data["action"] == 0:
                receive_data_from_mqtt()
                send_data()

                #signals
                def device_save(instance, **kwargs):
                    if (instance.user.id == self.token_id):
                        send_data()
                post_save.connect(device_save, sender=Gaschek_Device, weak=False)

                def user_save(instance, **kwargs):
                    if (instance.id == self.token_id):
                        publish_data_to_mqtt()
                post_save.connect(user_save, sender=User, weak=False)
                #signals

            data2 = encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8')
            
            if (client_data["action"] == 'a'):
                try:
                    data = get_device()
                    if (data.alarm == "on"):
                        data.alarm = "off"
                    else:
                        data.alarm = "on"
                    data.save()
                    publish_data_to_mqtt()
                except Exception:
                    self.send(bytes_data=data2)

            if (client_data["action"] == 'c'):
                try:
                    data = get_device()
                    if (data.call == "on"):
                        data.call = "off"
                    else:
                        data.call = "on"
                    data.save()
                    publish_data_to_mqtt()
                except Exception:
                    self.send(bytes_data=data2)

            if (client_data["action"] == 't'):
                try:
                    data = get_device()
                    if (data.text == "on"):
                        data.text = "off"
                    else:
                        data.text = "on"
                    data.save()
                    publish_data_to_mqtt()
                except Exception:
                    self.send(bytes_data=data2)

            if (client_data["action"] == 'i'):
                try:
                    data = get_device()
                    if (data.indicator == "on"):
                        data.indicator = "off"
                    else:
                        data.indicator = "on"
                    data.save()
                    publish_data_to_mqtt()
                except Exception:
                    self.send(bytes_data=data2)

        except Exception:
            self.send(bytes_data=encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8'))


# class ToggleDetailsConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         token = self.scope['query_string'].decode('utf-8')
#         try:
#             payload = jwt_decoder(token)
#             self.token_id = payload['id']
#             self.client = connect_to_mqtt_broker(self.token_id)
#             await self.accept()
#         except Exception:
#             await self.close()

#     async def disconnect(self, close_code):
#         await self.close()

#     async def receive(self, bytes_data):
#         try:
#             convert_byte_to_text = bytes_data.decode('utf-8')
#             decrypted_text_data = decrypt(convert_byte_to_text)
#             client_data = json.loads(decrypted_text_data)

#             if client_data["action"] == 'cnt':
#                 data = encrypt(json.dumps({
#                     'msg': 200
#                 })).encode('utf-8')
#                 await self.send(bytes_data=data)

#             data2 = encrypt(json.dumps({
#                 'msg': 400
#             })).encode('utf-8')

#             data = await sync_to_async(Gaschek_Device.objects.get)(user=self.token_id)
#             if (client_data["action"] == 'a'):
#                 try:
#                     message = None
#                     if (data.alarm == "on"):
#                         data.alarm = "off"
#                         message = "off"
#                     else:
#                         data.alarm = "on"
#                         message = "on"

#                     self.client.publish(str(self.token_id), payload=json.dumps({
#                         "alarm": message
#                     }), qos=0)
#                     await sync_to_async(data.save)()
#                 except Exception:
#                     await self.send(bytes_data=data2)

#             if (client_data["action"] == 'c'):
#                 try:
#                     if (data.call == "on"):
#                         data.call = "off"
#                     else:
#                         data.call = "on"
#                     await sync_to_async(data.save)()

#                 except Exception:
#                     self.send(bytes_data=data2)

#             if (client_data["action"] == 't'):
#                 try:
#                     if (data.text == "on"):
#                         data.text = "off"
#                     else:
#                         data.text = "on"
#                     await sync_to_async(data.save)()
#                 except Exception:
#                     await self.send(bytes_data=data2)

#             if (client_data["action"] == 'i'):
#                 try:
#                     if (data.indicator == "on"):
#                         data.indicator = "off"
#                     else:
#                         data.indicator = "on"
#                     await sync_to_async(data.save)()

#                 except Exception:
#                     await self.send(bytes_data=data2)

#         except Exception:
#             data2 = encrypt(json.dumps({
#                 'msg': 400
#             })).encode('utf-8')
#             await self.send(bytes_data=data2)


# class GasDetailsDeviceConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()

#     def disconnect(self, close_code):
#         self.close()
#         # pass

#     def receive(self, text_data):
#         client_data = json.loads(text_data)

#         if (client_data["action"] == 'connect'):
#             def send_data():
#                 user = User.objects.get(id=client_data['user_id'])
#                 data = Gaschek_Device.objects.get(user=user)
#                 serializer = Gaschek_Get_Serializer(data)
#                 serializer2 = UserSerializer(user)

#                 self.send(json.dumps({
#                     'call': serializer.data['call'],
#                     'alarm': serializer.data['alarm'],
#                     'text': serializer.data['text'],
#                     'country_code': serializer2.data['country_code'],
#                     'number_one': serializer2.data['phonenumber_ordering'],
#                     'number_two': serializer2.data['phonenumber_gaschek_device_1'],
#                     'number_three': serializer2.data['phonenumber_gaschek_device_2'],
#                     'number_four': serializer2.data['phonenumber_gaschek_device_3']
#                 }))
#             send_data()

#             def give_data(instance, **kwargs):
#                 if (instance.user.id == client_data['user_id']):
#                     send_data()
#             post_save.connect(give_data, sender=Gaschek_Device, weak=False)

#             try:
#                 data = Gaschek_Device.objects.get(user=self.token_id)
#                 if (data.indicator == "on"):
#                     data.indicator = "off"
#                 else:
#                     data.indicator = "on"
#                 data.save()

#             except Exception:
#                 self.send(json.dumps({
#                     'msg': 400
#                 }))


# class SendDeviceDetailsConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.close()
#         # pass

#     async def receive(self, text_data):
#         client_data = json.loads(text_data)

#         user = await sync_to_async(User.objects.get)(id=client_data['user_id'])
#         gaschek_device = await sync_to_async(Gaschek_Device.objects.get)(user=user)

#         gaschek_device.cylinder = client_data['cylinder']
#         gaschek_device.gas_mass = client_data['gas_mass']
#         gaschek_device.gas_level = client_data['gas_level']
#         gaschek_device.battery_level = client_data['battery_level']
#         await sync_to_async(gaschek_device.save)()
