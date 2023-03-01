import json
from accounts.models import User, Gas_Dealer
from orders.models import Gas_orders
from orders.serializers import Order_Serializer
from channels.generic.websocket import WebsocketConsumer
from django.db.models.signals import post_save
from functions.encryption import jwt_decoder


class GasDealerOrdersConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        self.close()

    def receive(self, text_data):
        client_data = json.loads(text_data)

        def send_data():
            try:
                payload = jwt_decoder(client_data['token'])
                user = User.objects.get(id=payload['id'])
                gas_dealer = Gas_Dealer.objects.get(user=user)
                orders = Gas_orders.objects.filter(
                    gas_dealer=gas_dealer).order_by('created_at').reverse()
                user_pending = Gas_orders.objects.filter(
                    gas_dealer=gas_dealer, user_confirmed=False, dealer_confirmed=True)
                dealer_pending = Gas_orders.objects.filter(
                    gas_dealer=gas_dealer, dealer_confirmed=False)
                serializer = Order_Serializer(orders, many=True)

                self.send(json.dumps({
                    'message': serializer.data,
                    'user_pending': len(user_pending),
                    'dealer_pending': len(dealer_pending),
                }))
            except Gas_orders.DoesNotExist:
                self.send(json.dumps({
                    'message': 'model_does_not_exist'
                }))  
            except Exception as e:
                self.send(json.dumps({
                    'message': 400
                }))  

        def give_data(**kwargs):
            send_data()
        post_save.connect(give_data, sender=Gas_orders, weak=False)
