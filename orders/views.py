from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from accounts.models import User, Gas_Dealer
from accounts.serializers import GasDealerSearchSerializer
from .models import Gas_orders
from accounts.models import Cylinder_Price, Delivery_Fee
from .serializers import (
    Cylinder_Price_Serializer,
    Order_Serializer,
    Delivery_Fee_Serializer,
)
from functions.encryption import auth_decoder, encrypt
from accounts.utils.auth_utils import jwt_required
from functions.CustomQuery import get_if_exists
import json
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page


@method_decorator(gzip_page, name="dispatch")
class AllGasDealersAPI(APIView):
    def get(self, request):
        gas_dealers = Gas_Dealer.objects.filter(
            state=request.query_params["state"], is_verified=True
        )

        serializer = GasDealerSearchSerializer(gas_dealers, many=True)

        return Response(encrypt(json.dumps({"status": 200, "data": serializer.data})))


@method_decorator(gzip_page, name="dispatch")
class Create_Cylinder_Price(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            cylinder = get_if_exists(
                Cylinder_Price, gas_dealer=gas_dealer, cylinder=request.data["cylinder"]
            )
            if cylinder:
                return Response(
                    encrypt(
                        json.dumps({"status": 400, "message": "duplicate cylinders"})
                    )
                )

            Cylinder_Price.objects.create(
                gas_dealer=gas_dealer,
                cylinder=request.data["cylinder"],
                price=request.data["price"],
            )
            cylinder_price = Cylinder_Price.objects.filter(gas_dealer=gas_dealer)
            serializer = Cylinder_Price_Serializer(cylinder_price, many=True)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception:
            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 400,
                        }
                    )
                )
            )

    # to delete cylinder_price
    @method_decorator(jwt_required(token_type="access"))
    def patch(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            cylinder = Cylinder_Price.objects.get(id=request.data["id"])
            cylinder.delete()

            cylinder_price = Cylinder_Price.objects.filter(gas_dealer=gas_dealer)
            serializer = Cylinder_Price_Serializer(cylinder_price, many=True)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception:
            return Response(
                encrypt(json.dumps({"status": 400, "message": "error deleting"}))
            )


@method_decorator(gzip_page, name="dispatch")
class Get_Cylinder_Price(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def get(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            cylinder_price = Cylinder_Price.objects.filter(gas_dealer=gas_dealer)
            serializer = Cylinder_Price_Serializer(cylinder_price, many=True)
            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception:
            return Response(encrypt(json.dumps({"status": 400, "message": "error"})))


@method_decorator(gzip_page, name="dispatch")
class Create_Delivery_Fee(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            fee = get_if_exists(Delivery_Fee, gas_dealer=gas_dealer)
            if fee:
                return Response(
                    encrypt(
                        json.dumps({"status": 400, "message": "duplicate delivery fee"})
                    )
                )

            Delivery_Fee.objects.create(
                gas_dealer=gas_dealer, price=request.data["price"]
            )
            d_fee = Delivery_Fee.objects.filter(gas_dealer=gas_dealer)
            serializer = Delivery_Fee_Serializer(d_fee, many=True)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception:
            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 400,
                        }
                    )
                )
            )

    # to delete cylinder_price
    @method_decorator(jwt_required(token_type="access"))
    def patch(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            fee = Delivery_Fee.objects.get(id=request.data["id"])
            fee.delete()

            d_fee = Delivery_Fee.objects.filter(gas_dealer=gas_dealer)
            serializer = Delivery_Fee_Serializer(d_fee, many=True)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception:
            return Response(
                encrypt(json.dumps({"status": 400, "message": "error deleting"}))
            )


@method_decorator(gzip_page, name="dispatch")
class Get_Delivery_Fee(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def get(self, request):
        try:

            user = User.objects.get(id=request.payload["id"])
            gas_dealer = Gas_Dealer.objects.get(user=user)

            d_fee = Delivery_Fee.objects.filter(gas_dealer=gas_dealer)
            serializer = Delivery_Fee_Serializer(d_fee, many=True)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception:
            return Response(encrypt(json.dumps({"status": 400, "message": "error"})))


@method_decorator(gzip_page, name="dispatch")
class Get_orders(APIView, LimitOffsetPagination):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = User.objects.get(id=request.request.payload["id"])

            if not user.is_dealer is True:
                orders = Gas_orders.objects.filter(user=user).order_by("-created_at")
                results = self.paginate_queryset(orders, request, view=self)
                serializer = Order_Serializer(results, many=True)
                return self.get_paginated_response(encrypt(json.dumps(serializer.data)))
            gas_dealer = Gas_Dealer.objects.get(user=user)
            orders = Gas_orders.objects.filter(gas_dealer=gas_dealer).order_by(
                "-created_at"
            )
            user_pending = Gas_orders.objects.filter(
                gas_dealer=gas_dealer, user_confirmed=False, dealer_confirmed=True
            )
            dealer_pending = Gas_orders.objects.filter(
                gas_dealer=gas_dealer, dealer_confirmed=False
            )
            serializer = Order_Serializer(orders, many=True)
            return Response(
                encrypt(
                    json.dumps(
                        {
                            "user_pending": len(user_pending),
                            "dealer_pending": len(dealer_pending),
                            "data": serializer.data,
                        }
                    )
                )
            )
        except Exception:
            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 400,
                        }
                    )
                )
            )


@method_decorator(gzip_page, name="dispatch")
class GasDealer_SearchAPI(APIView):
    def get(self, request):
        try:
            search = Gas_Dealer.objects.filter(
                state=request.query_params["state"],
                company_name__icontains=request.query_params["search"],
            )

            serializer = GasDealerSearchSerializer(search, many=True)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception:
            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 400,
                        }
                    )
                )
            )


@method_decorator(gzip_page, name="dispatch")
class Confirm_OrderAPI(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])

            if request.data["user_type"] == "dealer":
                gas_dealer = Gas_Dealer.objects.get(user=user)
                order = Gas_orders.objects.get(
                    id=request.data["id"], gas_dealer=gas_dealer
                )
                order.dealer_confirmed = True
                order.save()

                return Response(encrypt(json.dumps({"status": 200})))
            else:
                order = Gas_orders.objects.get(id=request.data["id"], user=user)
                order.user_confirmed = True
                order.save()

                return Response(encrypt(json.dumps({"status": 200})))

        except Exception:
            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 400,
                        }
                    )
                )
            )
