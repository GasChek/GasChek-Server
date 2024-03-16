from .serializers import Gaschek_Device_Serializer
from accounts.models import User
from .models import Gaschek_Device
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save
from functions.encryption import auth_decoder, encrypt, decrypt
from dotenv import load_dotenv
import random
import string
import json
load_dotenv()
from django.utils import timezone
# MQTT
import paho.mqtt.client as mqtt_client
from paho import mqtt
from mqtt.models import Mqtt_Servers
# MQTT


class GasDetailsConsumer(WebsocketConsumer):
    def connect(self):
        try:
            token = self.scope['query_string'].decode('utf-8')
            payload = auth_decoder(token)
            self.client_data = None
            self.client = None
            self.device_id = payload['device_id']
            self.user_id = self.get_device().user.id
            self.client = self.connect_to_mqtt_broker(self.device_id)
            self.accept()
        except Exception:
            self.close()

    def disconnect(self, close_code):
        if self.client_data:
            self.disconnect_signals()
        if self.client:
            self.client.unsubscribe(self.device_id)
            self.client.loop_stop()
        self.close()

    def receive(self, bytes_data):
        try:
            convert_byte_to_text = bytes_data.decode('utf-8')
            decrypted_text_data = decrypt(convert_byte_to_text)
            self.client_data = json.loads(decrypted_text_data)

            if 'action' in self.client_data:
                if self.client_data["action"] == 0:
                    self.receive_data_from_mqtt()
                    self.setup_signals()
                    self.send_data()
                else:
                    self.handle_client_action(self.client_data)
            else:
                self.handle_client_action(self.client_data)

        except Exception:
            self.send(bytes_data=encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8'))

    #functions 
    def generate_random_text(self, length=10):
        characters = string.ascii_letters + string.digits
        random_text = ''.join(random.choice(characters) for i in range(length))
        return random_text
        
    def connect_to_mqtt_broker(self, topic):
        mqtt_server = Mqtt_Servers.objects.get(active=True)
        client = mqtt_client.Client(client_id=f'GasChek-client-{self.generate_random_text()}', 
                             userdata=None, 
                             protocol=mqtt_client.MQTTv5,
                             callback_api_version=mqtt_client.CallbackAPIVersion.VERSION1)
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(mqtt_server.user, mqtt_server.password)
        client.connect(mqtt_server.server_url, mqtt_server.port)
        client.subscribe(str(topic), qos=mqtt_server.qos)
        return client
    
    def get_device(self):
        return Gaschek_Device.objects.get(device_id=self.device_id)
             
    def send_data(self):
        serializer = Gaschek_Device_Serializer(self.get_device())
        encrypted_data = encrypt(json.dumps(serializer.data))        

        data = encrypt(json.dumps({
            'msg': encrypted_data
        })).encode('utf-8')
        self.send(bytes_data=data)

    def device_save(self, instance, **kwargs):
        if (instance.device_id == self.device_id):
            self.send_data()

    # def user_save(self, instance, **kwargs):
    #     if (instance.id == self.user_id):
    #         self.publish_data_to_mqtt()

    def disconnect_signals(self):
        post_save.disconnect(self.device_save, sender=Gaschek_Device)
        # post_save.disconnect(self.user_save, sender=User)

    def setup_signals(self):
        post_save.connect(self.device_save, sender=Gaschek_Device, weak=False)
        # post_save.connect(self.user_save, sender=User, weak=False)

    def publish_data_to_mqtt(self, device):
        payload = json.dumps({
            'cylinder': str(device.cylinder),
            'alarm': device.alarm,
            'call': device.call,
            'text': device.text,
            'indicator': device.indicator,
            'number_one': f'{device.country_code}{device.phonenumber_one}',
            'number_two': f'{device.country_code}{device.phonenumber_two}',
            'number_three': f'{device.country_code}{device.phonenumber_three}'
        })
        self.client.publish(self.device_id, payload=payload, qos=0)

    def receive_data_from_mqtt(self):
        def on_message(client, userdata, msg):
            device_data = json.loads(msg.payload.decode('utf-8'))
            if "gas_mass" in device_data:
                device = self.get_device()
                device.cylinder = device_data["cylinder"]
                device.gas_mass = device_data["gas_mass"]
                device.gas_level = device_data["gas_level"]
                device.battery_level = device_data["battery_level"]
                device.indicator = device_data["indicator"]
                device.device_update_time = timezone.now()
                device.save()
        self.client.on_message = on_message
        self.client.loop_start()       

    def handle_client_action(self, client_data):
        try:
            device = self.get_device()
            if 'action' in client_data:
                action_to_attribute = {
                    'a': 'alarm',
                    'c': 'call',
                    't': 'text',
                    'i': 'indicator'
                }
                action = client_data["action"]
                if action in action_to_attribute:
                    attribute = action_to_attribute[action]
                    setattr(device, attribute, 'off' if getattr(device, attribute) == 'on' else 'on')
                    device.save()
            elif 'cylinder' in client_data:
                device.cylinder = client_data['cylinder']
                device.save()    
            else:
                numbers = client_data['numbers']
                device.country_code  = numbers['country_code']
                device.phonenumber_one = numbers['number_one']
                device.phonenumber_two = numbers['number_two']
                device.phonenumber_three = numbers['number_three']
                device.save()
            self.publish_data_to_mqtt(device)
        except Exception as e:
            print(e)
            self.send(bytes_data= encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8'))

class GasDetailsConsumerMobileApp(WebsocketConsumer):
    def connect(self):
        try:
            token = self.scope['query_string'].decode('utf-8')
            payload = auth_decoder(token)
            self.client_data = None
            self.client = None
            self.device_id = payload['device_id']
            self.user_id = self.get_device().user.id
            self.client = self.connect_to_mqtt_broker(self.device_id)
            self.accept()
        except Exception as e:
            print(e)
            self.close()

    def disconnect(self, close_code):
        if self.client_data:
            self.disconnect_signals()
        if self.client:
            self.client.unsubscribe(self.device_id)
            self.client.loop_stop()
        self.close()

    def receive(self, text_data):
        try:
            decrypted_text_data = decrypt(text_data)
            self.client_data = json.loads(decrypted_text_data)

            if 'action' in self.client_data:
                if self.client_data["action"] == 0:
                    self.receive_data_from_mqtt()
                    self.setup_signals()
                    self.send_data()
                else:
                    self.handle_client_action(self.client_data)
            else:
                self.handle_client_action(self.client_data)

        except Exception:
            self.send(encrypt(json.dumps({
                'msg': 400
            })))

    #functions 
    def generate_random_text(self, length=10):
        characters = string.ascii_letters + string.digits
        random_text = ''.join(random.choice(characters) for i in range(length))
        return random_text
        
    def connect_to_mqtt_broker(self, topic):
        mqtt_server = Mqtt_Servers.objects.get(active=True)
        client = mqtt_client.Client(client_id=f'GasChek-client-{self.generate_random_text()}', 
                             userdata=None, 
                             protocol=mqtt_client.MQTTv5,
                             callback_api_version=mqtt_client.CallbackAPIVersion.VERSION1)
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(mqtt_server.user, mqtt_server.password)
        client.connect(mqtt_server.server_url, mqtt_server.port)
        client.subscribe(str(topic), qos=mqtt_server.qos)
        return client
    
    def get_device(self):
        return Gaschek_Device.objects.get(device_id=self.device_id)
             
    def send_data(self):
        serializer = Gaschek_Device_Serializer(self.get_device())
        encrypted_data = encrypt(json.dumps(serializer.data))        

        data = encrypt(json.dumps({
            'msg': encrypted_data
        }))
        self.send(data)

    def device_save(self, instance, **kwargs):
        if (instance.device_id == self.device_id):
            self.send_data()

    # def user_save(self, instance, **kwargs):
    #     if (instance.id == self.user_id):
    #         self.publish_data_to_mqtt()

    def disconnect_signals(self):
        post_save.disconnect(self.device_save, sender=Gaschek_Device)
        # post_save.disconnect(self.user_save, sender=User)

    def setup_signals(self):
        post_save.connect(self.device_save, sender=Gaschek_Device, weak=False)
        # post_save.connect(self.user_save, sender=User, weak=False)

    def publish_data_to_mqtt(self, device):
        payload = json.dumps({
            'cylinder': str(device.cylinder),
            'alarm': device.alarm,
            'call': device.call,
            'text': device.text,
            'indicator': device.indicator,
            'number_one': f'{device.country_code}{device.phonenumber_one}',
            'number_two': f'{device.country_code}{device.phonenumber_two}',
            'number_three': f'{device.country_code}{device.phonenumber_three}'
        })
        self.client.publish(self.device_id, payload=payload, qos=0)

    def receive_data_from_mqtt(self):
        def on_message(client, userdata, msg):
            device_data = json.loads(msg.payload.decode('utf-8'))
            if "gas_mass" in device_data:
                device = self.get_device()
                device.cylinder = device_data["cylinder"]
                device.gas_mass = device_data["gas_mass"]
                device.gas_level = device_data["gas_level"]
                device.battery_level = device_data["battery_level"]
                device.indicator = device_data["indicator"]
                device.device_update_time = timezone.now()
                device.save()
        self.client.on_message = on_message
        self.client.loop_start()       

    def handle_client_action(self, client_data):
        try:
            device = self.get_device()
            if 'action' in client_data:
                action_to_attribute = {
                    'a': 'alarm',
                    'c': 'call',
                    't': 'text',
                    'i': 'indicator'
                }
                action = client_data["action"]
                if action in action_to_attribute:
                    attribute = action_to_attribute[action]
                    setattr(device, attribute, 'off' if getattr(device, attribute) == 'on' else 'on')
                    device.save()
            elif 'cylinder' in client_data:
                device.cylinder = client_data['cylinder']
                device.save()    
            else:
                numbers = client_data['numbers']
                device.country_code  = numbers['country_code']
                device.phonenumber_one = numbers['number_one']
                device.phonenumber_two = numbers['number_two']
                device.phonenumber_three = numbers['number_three']
                device.save()
            self.publish_data_to_mqtt(device)
        except Exception as e:
            print(e)
            self.send(bytes_data= encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8'))



class GasDetailsConsumerEmulation(WebsocketConsumer):
    def connect(self):
        try:
            token = self.scope['query_string'].decode('utf-8')
            payload = auth_decoder(token)
            self.client_data = None
            self.client = None
            self.device_id = payload['device_id']
            self.user_id = self.get_device().user.id
            self.accept()
        except Exception as e:
            print(e)
            self.close()

    def disconnect(self, close_code):
        # if self.client_data:
        self.disconnect_signals()
        self.close()

    def receive(self, bytes_data):
        try:
            convert_byte_to_text = bytes_data.decode('utf-8')
            decrypted_text_data = decrypt(convert_byte_to_text)
            self.client_data = json.loads(decrypted_text_data)

            if 'action' in self.client_data:
                if self.client_data["action"] == 0:
                    self.send_data()
                    self.setup_signals()
                else:
                    self.handle_client_action(self.client_data)
            else:
                self.handle_client_action(self.client_data)

        except Exception:
            self.send(bytes_data=encrypt(json.dumps({
                'msg': 400
            })).encode('utf-8'))

    #functions 
    def generate_random_text(self, length=10):
        characters = string.ascii_letters + string.digits
        random_text = ''.join(random.choice(characters) for i in range(length))
        return random_text
    
    def get_device(self):
        return Gaschek_Device.objects.get(device_id=self.device_id)
             
    def send_data(self):
        serializer = Gaschek_Device_Serializer(self.get_device())
        encrypted_data = encrypt(json.dumps(serializer.data))        

        data = encrypt(json.dumps({
            'msg': encrypted_data
        })).encode('utf-8')
        self.send(bytes_data=data)

    def device_save(self, instance, **kwargs):
        if (instance.device_id == self.device_id):
            self.send_data()

    # def user_save(self, instance, **kwargs):
    #     if (instance.id == self.user_id):
    #         self.publish_data_to_mqtt()

    def disconnect_signals(self):
        post_save.disconnect(self.device_save, sender=Gaschek_Device)
        # post_save.disconnect(self.user_save, sender=User)

    def setup_signals(self):
        post_save.connect(self.device_save, sender=Gaschek_Device, weak=False)
        # post_save.connect(self.user_save, sender=User, weak=False)

    def handle_client_action(self, client_data):
        if 'action' in client_data:
            action_to_attribute = {
                'a': 'alarm',
                'c': 'call',
                't': 'text',
                'i': 'indicator'
            }
            action = client_data["action"]
            if action in action_to_attribute:
                attribute = action_to_attribute[action]
                try:
                    device = self.get_device()
                    device.device_update_time = timezone.now()
                    setattr(device, attribute, 'off' if getattr(device, attribute) == 'on' else 'on')
                    device.save()
                except Exception as e:
                    print(e)
                    self.send(bytes_data= encrypt(json.dumps({
                        'msg': 400
                    })).encode('utf-8'))
        elif 'cylinder' in client_data:
            device = self.get_device()
            device.cylinder = client_data['cylinder']
            device.save()    
        else:
            device = self.get_device()
            numbers = client_data['numbers']
            device.country_code  = numbers['country_code']
            device.phonenumber_one = numbers['number_one']
            device.phonenumber_two = numbers['number_two']
            device.phonenumber_three = numbers['number_three']
            device.save()


# class ToggleDetailsConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         token = self.scope['query_string'].decode('utf-8')
#         try:
#             payload = auth_decoder(token)
#             self.device_id = payload['id']
#             self.client = connect_to_mqtt_broker(self.device_id)
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

#             data = await sync_to_async(Gaschek_Device.objects.get)(user=self.device_id)
#             if (client_data["action"] == 'a'):
#                 try:
#                     message = None
#                     if (data.alarm == "on"):
#                         data.alarm = "off"
#                         message = "off"
#                     else:
#                         data.alarm = "on"
#                         message = "on"

#                     self.client.publish(self.device_id, payload=json.dumps({
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
#                 data = Gaschek_Device.objects.get(user=self.device_id)
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