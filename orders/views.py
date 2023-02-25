from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User, Gas_Dealer
from accounts.serializers import GasDealerSearchSerializer
from .models import Cylinder_Price, Gas_orders, Delivery_Fee
from .serializers import (Cylinder_Price_Serializer,
                          Order_Serializer,
                          Delivery_Fee_Serializer)
from functions.encryption import jwt_decoder
# Create your views here.


class AllGasDealersAPI(APIView):
    def get(self, request):
        gas_dealers = Gas_Dealer.objects.filter(
            state=request.query_params['state'])

        serializer = GasDealerSearchSerializer(gas_dealers, many=True)

        return Response({
            'status': 200,
            'data': serializer.data
        })


class Create_Cylinder_Price(APIView):
    def post(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            cylinder = Cylinder_Price.objects.filter(
                gas_dealer=gas_dealer, cylinder=request.data["cylinder"]).first()
            if cylinder:
                return Response({
                    'status': 400,
                    'message': 'duplicate cylinders'
                })

            Cylinder_Price.objects.create(
                gas_dealer=gas_dealer,
                cylinder=request.data["cylinder"],
                price=request.data["price"]
            )
            cylinder_price = Cylinder_Price.objects.filter(
                gas_dealer=gas_dealer)
            serializer = Cylinder_Price_Serializer(cylinder_price, many=True)

            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception:
            return Response({
                'status': 400,
            })

    # to delete cylinder_price
    def patch(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            cylinder = Cylinder_Price.objects.get(id=request.data['id'])
            cylinder.delete()

            cylinder_price = Cylinder_Price.objects.filter(
                gas_dealer=gas_dealer)
            serializer = Cylinder_Price_Serializer(cylinder_price, many=True)

            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'error deleting'
            })


class Get_Cylinder_Price(APIView):
    def get(self, request):
        try:
            payload = jwt_decoder(request.query_params['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            cylinder_price = Cylinder_Price.objects.filter(
                gas_dealer=gas_dealer)
            serializer = Cylinder_Price_Serializer(cylinder_price, many=True)
            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'error'
            })


class Create_Delivery_Fee(APIView):
    def post(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            fee = Delivery_Fee.objects.filter(gas_dealer=gas_dealer).first()
            if fee:
                return Response({
                    'status': 400,
                    'message': 'duplicate delivery fee'
                })

            Delivery_Fee.objects.create(
                gas_dealer=gas_dealer,
                price=request.data["price"]
            )
            d_fee = Delivery_Fee.objects.filter(gas_dealer=gas_dealer)
            serializer = Delivery_Fee_Serializer(d_fee, many=True)

            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception:
            return Response({
                'status': 400,
            })
# to delete cylinder_price

    def patch(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            fee = Delivery_Fee.objects.get(id=request.data['id'])
            fee.delete()

            d_fee = Delivery_Fee.objects.filter(gas_dealer=gas_dealer)
            serializer = Delivery_Fee_Serializer(d_fee, many=True)

            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'error deleting'
            })


class Get_Delivery_Fee(APIView):
    def get(self, request):
        try:
            payload = jwt_decoder(request.query_params['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            d_fee = Delivery_Fee.objects.filter(gas_dealer=gas_dealer)
            serializer = Delivery_Fee_Serializer(d_fee, many=True)

            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'error'
            })


class Get_orders(APIView):
    def post(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            user = User.objects.get(id=payload['id'])

            if (user.is_dealer is True):
                gas_dealer = Gas_Dealer.objects.get(user=user)
                orders = Gas_orders.objects.filter(
                    gas_dealer=gas_dealer).order_by('created_at').reverse()
                pending = Gas_orders.objects.filter(
                    gas_dealer=gas_dealer, confirmed=False)
                serializer = Order_Serializer(orders, many=True)
                return Response({
                    'status': 200,
                    'pending': len(pending),
                    'data': serializer.data
                })

            else:
                orders = Gas_orders.objects.filter(
                    user=user).order_by('created_at').reverse()
                serializer = Order_Serializer(orders, many=True)
                return Response({
                    'status': 200,
                    'data': serializer.data
                })

        except Exception:
            return Response({
                'status': 400,
            })


class GasDealer_SearchAPI(APIView):
    def get(self, request):
        try:
            search = Gas_Dealer.objects.filter(state=request.query_params['state'],
                                               company_name__icontains=request.query_params['search'])

            serializer = GasDealerSearchSerializer(search, many=True)

            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception:
            return Response({
                'status': 400,
            })

class Confirm_OrderAPI(APIView):
    def post(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            order = Gas_orders.objects.get(
                id=request.data['id'], gas_dealer=gas_dealer)
            order.confirmed = True
            order.save()

            return Response({
                'status': 200
            })
        except Exception:
            return Response({
                'status': 400,
            })
