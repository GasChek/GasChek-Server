import json
from accounts.models import User, Gas_Dealer
from orders.models import Gas_orders
from orders.serializers import Order_Serializer
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save
from functions.encryption import auth_decoder, encrypt

class GasDealerOrdersConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close()

    def receive(self, text_data):
        try:
            client_data = json.loads(text_data)
            payload = auth_decoder(client_data['cnt'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)
            
            def send_data():
                try:
                    orders = Gas_orders.objects.filter(
                        gas_dealer=gas_dealer).order_by('-created_at')
                    user_pending = Gas_orders.objects.filter(
                        gas_dealer=gas_dealer, user_confirmed=False, dealer_confirmed=True)
                    dealer_pending = Gas_orders.objects.filter(
                        gas_dealer=gas_dealer, dealer_confirmed=False)
                    serializer = Order_Serializer(orders, many=True)
                    encrypted_data = encrypt(json.dumps(serializer.data))

                    self.send(json.dumps({
                        'msg': encrypted_data,
                        'u_p': len(user_pending),
                        'd_p': len(dealer_pending),
                    }))
                except Gas_orders.DoesNotExist:
                    self.send(json.dumps({
                        'msg': 400
                    }))  

            def give_data(instance, **kwargs):
                if(instance.gas_dealer.id == gas_dealer.id):
                    send_data()
            post_save.connect(give_data, sender=Gas_orders, weak=False)
        except Exception:
            self.send(json.dumps({
                'msg': 400
            }))  