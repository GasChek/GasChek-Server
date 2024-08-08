from .serializers import Gaschek_Device_Serializer
from .models import Gaschek_Device
from channels.generic.websocket import WebsocketConsumer
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

# This is built for both web and mobile consumers to share functions,
# to access functions, use the super().the_function_you_want()


class ConsumersMixin:
    def connect(self):
        token = self.scope["query_string"].decode("utf-8")
        payload = auth_decoder(token)
        self.client_data = None
        self.client = None
        self.device_id = payload["device_id"]
        self.user_id = self.get_device().user.id
        self.client = self.connect_to_mqtt_broker(self.device_id)

    def disconnect(self):
        if self.client:
            self.client.unsubscribe(self.device_id)
            self.client.loop_stop()

    def get_device(self):
        return Gaschek_Device.objects.get(device_id=self.device_id)

    def generate_random_text(self, length=10):
        characters = string.ascii_letters + string.digits
        random_text = "".join(random.choice(characters) for i in range(length))
        return random_text

    def connect_to_mqtt_broker(self, topic):
        mqtt_server = Mqtt_Servers.objects.get(active=True)
        client = mqtt_client.Client(
            client_id=f"GasChek-client-{self.generate_random_text()}",
            userdata=None,
            protocol=mqtt_client.MQTTv5,
            callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
        )
        client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        client.username_pw_set(mqtt_server.user, mqtt_server.password)
        client.connect(mqtt_server.server_url, mqtt_server.port)
        client.subscribe(str(topic), qos=mqtt_server.qos)
        return client

    def publish_data_to_mqtt(self, device):
        payload = json.dumps(
            {
                "cylinder": str(device.cylinder),
                "alarm": device.alarm,
                "call": device.call,
                "text": device.text,
                "indicator": device.indicator,
                "number_one": f"{device.country_code}{device.phonenumber_one}",
                "number_two": f"{device.country_code}{device.phonenumber_two}",
                "number_three": f"{device.country_code}{device.phonenumber_three}",
            }
        )
        print("sending to mqtt")
        self.client.publish(self.device_id, payload=payload, qos=0)

    def receive_data_from_mqtt(self):
        def on_connect(client, userdata, flags, reason_code, properties):
            if reason_code == 0:
                print(f"Connected to MQTT Broker! : {reason_code}")
            else:
                print(
                    f"Failed to connect, return code: {reason_code}",
                )

        def on_message(client, userdata, msg):
            device_data = json.loads(msg.payload.decode("utf-8"))
            if "gas_mass" in device_data:
                device = super().get_device()
                # device.cylinder = device_data["cylinder"]
                device.cylinder = 12.5
                device.gas_mass = device_data["gas_mass"]
                device.gas_level = device_data["gas_level"]
                device.battery_level = device_data["battery_level"]
                device.indicator = device_data["indicator"]
                device.device_update_time = timezone.now()
                device.save()

            self.send_data()

        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.loop_start()

    def handle_client_action(self, client_data):
        device = self.get_device()
        if "action" in client_data:
            action_to_attribute = {
                "a": "alarm",
                "c": "call",
                "t": "text",
                "i": "indicator",
            }
            action = client_data["action"]
            if action in action_to_attribute:
                attribute = action_to_attribute[action]
                setattr(
                    device,
                    attribute,
                    "off" if getattr(device, attribute) == "on" else "on",
                )
                device.save()
        elif "cylinder" in client_data:
            device.cylinder = client_data["cylinder"]
            device.save()
        else:
            numbers = client_data["numbers"]
            device.country_code = numbers["country_code"]
            device.phonenumber_one = numbers["number_one"]
            device.phonenumber_two = numbers["number_two"]
            device.phonenumber_three = numbers["number_three"]
            device.save()
        self.publish_data_to_mqtt(device)


class GasDetailsConsumerWeb(ConsumersMixin, WebsocketConsumer):
    def connect(self):
        try:
            super().connect()
            self.accept()
        except Exception:
            self.close()

    def disconnect(self, close_code):
        super().disconnect()

    def receive(self, bytes_data):
        try:
            convert_byte_to_text = bytes_data.decode("utf-8")
            decrypted_text_data = decrypt(convert_byte_to_text)
            self.client_data = json.loads(decrypted_text_data)

            if "action" in self.client_data:
                if self.client_data["action"] == 0:
                    super().receive_data_from_mqtt()
                    self.send_data()
                else:
                    self.handle_client_action(self.client_data)
            else:
                self.handle_client_action(self.client_data)

        except Exception:
            self.send(bytes_data=encrypt(json.dumps({"msg": 400})).encode("utf-8"))

    def send_data(self):
        serializer = Gaschek_Device_Serializer(super().get_device())
        encrypted_data = encrypt(json.dumps(serializer.data))
        data = encrypt(json.dumps({"msg": encrypted_data})).encode("utf-8")
        self.send(bytes_data=data)

    def device_save(self, instance, **kwargs):
        pass
        # if instance.device_id == self.device_id:
        #     self.send_data()

    def user_save(self, instance, **kwargs):
        pass
        # if (instance.id == self.user_id):
        #    self.publish_data_to_mqtt()

    def disconnect_signals(self):
        pass
        # post_save.disconnect(self.device_save, sender=Gaschek_Device)
        # post_save.disconnect(self.user_save, sender=User)

    def setup_signals(self):
        pass
        # post_save.connect(self.device_save, sender=Gaschek_Device, weak=False)
        # post_save.connect(self.user_save, sender=User, weak=False)

    def handle_client_action(self, client_data):
        try:
            super().handle_client_action(client_data)
        except Exception as e:
            print(e)
            self.send(bytes_data=encrypt(json.dumps({"msg": 400})).encode("utf-8"))


class GasDetailsConsumerMobile(ConsumersMixin, WebsocketConsumer):
    def connect(self):
        try:
            super().connect()
            self.accept()
        except Exception:
            self.close()

    def disconnect(self, close_code):
        super().disconnect()

    def receive(self, text_data):
        try:
            decrypted_text_data = decrypt(text_data)
            self.client_data = json.loads(decrypted_text_data)

            if "action" in self.client_data:
                print(self.client_data)
                if self.client_data["action"] == 0:
                    super().receive_data_from_mqtt()
                    self.send_data()
                else:
                    self.handle_client_action(self.client_data)
            else:
                self.handle_client_action(self.client_data)

        except Exception:
            self.send(encrypt(json.dumps({"msg": 400})))

    def send_data(self):
        serializer = Gaschek_Device_Serializer(super().get_device())
        encrypted_data = encrypt(json.dumps(serializer.data))
        data = encrypt(json.dumps({"msg": encrypted_data}))
        self.send(data)

    def device_save(self, instance, **kwargs):
        pass
        # if instance.device_id == self.device_id:
        #    self.send_data()

    def user_save(self, instance, **kwargs):
        pass
        # if (instance.id == self.user_id):
        #    self.publish_data_to_mqtt()

    def disconnect_signals(self):
        pass
        # post_save.disconnect(self.device_save, sender=Gaschek_Device)
        # post_save.disconnect(self.user_save, sender=User)

    def setup_signals(self):
        pass
        # post_save.connect(self.device_save, sender=Gaschek_Device, weak=False)
        # post_save.connect(self.user_save, sender=User, weak=False)

    def handle_client_action(self, client_data):
        try:
            super().handle_client_action(client_data)
        except Exception as e:
            print(e)
            self.send(encrypt(json.dumps({"msg": 400})))
