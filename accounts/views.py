import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    LogInSerializer,
    VerifyAccountSerializer,
    DealerLogInSerializer,
    UserSerializer,
    GasDealerSerializer,
)
from .models import (
    User,
    Gas_Dealer,
    Token,
    Abandoned_Subaccounts,
    Cylinder_Price,
    Delivery_Fee,
)
from orders.serializers import Cylinder_Price_Serializer, Delivery_Fee_Serializer
from django.contrib.auth.models import update_last_login
from functions.emails import HandleEmail
from functions.encryption import auth_decoder, encrypt
from functions.CustomQuery import get_if_exists
from external_api.paystack import create_subaccount, update_subaccount
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from .utils.auth_utils import (
    generate_auth_token,
    jwt_required,
    get_tokens,
)


class RefreshTokenView(APIView):
    @method_decorator(jwt_required(token_type="refresh"))
    def post(self, request):
        user = get_if_exists(User, id=request.payload["id"])
        if not user:
            response_data = {
                "msg": "Invalid auth",
            }
            response = Response(response_data, status=status.HTTP_403_FORBIDDEN)
            if request.data["platform"] == "web":
                response.delete_cookie("refresh")
            return response
        return Response(
            {
                "access": generate_auth_token(user, "access", "user"),
            }
        )


@method_decorator(gzip_page, name="dispatch")
class SignUpAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                encrypt(
                    json.dumps(
                        {
                            "msg": "User with this email already exists.",
                        }
                    )
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        user = User.objects.get(email=serializer.data["email"])
        HandleEmail(user, "create").start()
        return Response(
            encrypt(
                json.dumps(
                    {
                        "token": generate_auth_token(user, "verification", "user"),
                    }
                )
            )
        )
        

@method_decorator(gzip_page, name="dispatch")
class VerifyOTP(APIView):
    @method_decorator(jwt_required(token_type="verification"))
    def post(self, request):
        try:
            serializer = VerifyAccountSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = get_if_exists(User, id=request.payload["id"])
            if not user:
                return Response(
                    {
                        "msg": "Invalid user",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user_token = Token.objects.get(user=user)
            if serializer.data["otp"] != user_token.otp:
                return Response(
                    {
                        "msg": "Invalid otp",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.is_verified = True
            user.save()
            response = Response()
            tokens = get_tokens(user, "user")
            if request.data["platform"] == "web":
                response.data = {"access": tokens["access"]}
                response.set_cookie(
                    key="refresh",
                    value=tokens["refresh"],
                    httponly=True,
                    samesite="None",
                    secure=True,  # Use True in production with HTTPS
                )
            else:
                response.data = tokens
            return response
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@method_decorator(gzip_page, name="dispatch")
class Resend_Otp(APIView):
    def post(self, request):
        user = User.objects.get(email=request.data["email"])
        HandleEmail(user, "update").start()
        return Response(
            {
                "token": generate_auth_token(user, "verification", "user"),
            }
        )

@method_decorator(gzip_page, name="dispatch")
class LoginAPI(APIView):
    def error_res(self):
        return Response(
            {"msg": "Invalid email or password"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def post(self, request):
        serializer = LogInSerializer(data=request.data)

        if not serializer.is_valid():
            return self.error_res()

        email = serializer.data["email"].lower()
        password = serializer.data["password"]
        user = get_if_exists(User, email=email)

        if not user or not user.check_password(password) or user.is_dealer is True:
            return self.error_res()

        if user.is_verified is False:
            return Response(
                {
                    "token": generate_auth_token(user, "verification", "user"),
                },
                status=status.HTTP_202_ACCEPTED,
            )
        update_last_login(None, user)
        response = Response()
        tokens = get_tokens(user, "user")
        if request.data["platform"] == "web":
            response.data = {"access": tokens["access"]}
            response.set_cookie(
                key="refresh",
                value=tokens["refresh"],
                httponly=True,
                samesite="None",
                secure=True,  # Use True in production with HTTPS
            )
        else:
            response.data = tokens
        return response


# CHECK IF ACCOUNT IS USER OR GAS DEALER
@method_decorator(gzip_page, name="dispatch")
class AccountViewAPI(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def get(self, request):
        try:
            return Response(
                {
                    "account_type": request.payload["account_type"],
                }
            )
        except Exception as e:
            print(e)
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# CHECK IF ACCOUNT IS USER OR GAS DEALER
@method_decorator(gzip_page, name="dispatch")
class ForgotPasswordAPI(APIView):
    def post(self, request):
        try:
            user = get_if_exists(User, email=request.data["email"])
            if not user:
                return Response({"msg": "ok"})

            HandleEmail(user, "update").start()
            token = generate_auth_token(user, "verification", "user")
            return Response({"token": token})
        except Exception as e:
            print(e)
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class ChangePasswordAPI(APIView):
    @method_decorator(jwt_required(token_type="verification"))
    def post(self, request):
        if request.data["p"] != request.data["p2"]:
            return Response(
                {"msg": "Password does not match"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_if_exists(User, id=request.payload["id"])
        if not user:
            return Response(
                {"msg": "error"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        token = Token.objects.get(user=user)
        if token.otp != int(request.data["otp"]):
            return Response(
                {"msg": "Invalid otp"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(request.data["p"])
        user.is_verified = True
        user.save()
        return Response(
            {
                "msg": "ok",
            }
        )


@method_decorator(gzip_page, name="dispatch")
class UserViewAPI(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])
            serializer = UserSerializer(user)
            encrypted_data = encrypt(json.dumps(serializer.data))

            return Response(
                {
                    "data": encrypted_data,
                }
            )
        except Exception as e:
            print(e)
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class UpdateUserAPI(APIView):
    @method_decorator(jwt_required(token_type="access"))
    def post(self, request):
        try:
            user = User.objects.get(id=request.payload["id"])
            if not user:
                return Response(
                    {"msg": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
                )

            user.first_name = request.data.get("first_name", user.first_name)
            user.last_name = request.data.get("last_name", user.last_name)
            user.country_code = request.data.get("country_code", user.country_code)
            user.phonenumber = request.data.get("phonenumber", user.phonenumber)
            user.address = request.data.get("address", user.address)
            user.state = request.data.get("state", user.state)

            user.save()
            serializer = UserSerializer(user)

            return Response(
                encrypt(
                    json.dumps(
                        {
                            "data": serializer.data,
                        }
                    )
                )
            )
        except Exception as e:
            print(e)
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(gzip_page, name="dispatch")
class LogoutAPIView(APIView):
    @method_decorator(jwt_required(token_type="refresh"))
    def post(self, request):
        try:
            user = get_if_exists(User, id=request.payload["id"])

            if not user:
                return Response(
                    {"msg": "Not Authorized"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            response = Response({"msg": "ok"})
            if request.data["platform"] == "web":
                response.delete_cookie("refresh")
            return response
        except Exception as e:
            print(str(e))
            return Response(
                {"msg": "Server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# USER


# DEALER
@method_decorator(gzip_page, name="dispatch")
class CreateGasDealerAPI(APIView):
    def post(self, request):
        user = get_if_exists(User, email=request.data["email"])

        if user:
            if user.is_verified is True:
                return Response(
                    {
                        "msg": "Email already exists",
                    }
                )
            else:
                gas_dealer = get_if_exists(Gas_Dealer, user=user)
                Abandoned_Subaccounts.objects.create(
                    company_name=gas_dealer.company_name,
                    subaccount_code=gas_dealer.subaccount_code,
                    subaccount_id=gas_dealer.subaccount_id,
                )
                user.delete()

        gas_dealer = get_if_exists(
            Gas_Dealer, company_name=request.data["company_name"]
        )
        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response(
                    {
                        "msg": "Company name already exists",
                    }
                )

        gas_dealer = get_if_exists(Gas_Dealer, phonenumber=request.data["phonenumber"])

        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response(
                    {
                        "msg": "Phonenumber already exists",
                    }
                )

        gas_dealer = get_if_exists(
            Gas_Dealer, account_number=request.data["account_number"]
        )

        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response(
                    {
                        "msg": "Account Number already exists",
                    }
                )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            abandoned_subaccount = get_if_exists(
                Abandoned_Subaccounts, company_name=request.data["company_name"]
            )

            if abandoned_subaccount:
                response = update_subaccount(
                    abandoned_subaccount.subaccount_code,
                    request.data["company_name"],
                    request.data["bank"],
                    str(request.data["account_number"]),
                )
                if response["status"] is True:
                    abandoned_subaccount.delete()

            else:
                percentage_charge = 2
                response = create_subaccount(
                    request.data["company_name"],
                    request.data["bank"],
                    str(request.data["account_number"]),
                    percentage_charge,
                )

            if response["status"] is True:
                serializer.save()
                response = response["data"]

                user = User.objects.get(email=serializer.data["email"])
                Gas_Dealer.objects.create(
                    user=user,
                    company_name=request.data["company_name"],
                    state=request.data["state"],
                    phonenumber=request.data["phonenumber"],
                    address=request.data["address"],
                    account_number=request.data["account_number"],
                    longitude=request.data["longitude"],
                    latitude=request.data["latitude"],
                    bank_name=response["settlement_bank"],
                    bank_code=request.data["bank"],
                    percentage_charge=response["percentage_charge"],
                    subaccount_code=response["subaccount_code"],
                    subaccount_id=response["id"],
                )
                HandleEmail(user, "create").start()

                return Response(
                    {
                        "status": 200,
                        "data": serializer.data["email"],
                    }
                )

            else:
                return Response({"status": 500, "response": response})

        return Response(
            {
                "msg": "Something went wrong",
            }
        )


@method_decorator(gzip_page, name="dispatch")
class Verify_Otp(APIView):
    def post(self, request):
        payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
        user = get_if_exists(User, id=payload["id"])
        if not user or user.is_verified is True:
            return Response({"msg": "Invaild email"})

        token = get_if_exists(Token, user=user)
        if not token:
            return Response({"msg": "Invaild email"})

        if token.otp != request.data["otp"]:
            return Response({"msg": "Invaild otp"})

        response = {}
        response["status"] = 200

        if user.is_dealer:
            gas_dealer = Gas_Dealer.objects.get(user=user)
            user.is_verified = True
            gas_dealer.is_verified = True
            user.save()
            gas_dealer.save()
            response["type"] = "dealer"
        else:
            user.is_verified = True
            user.save()
            response["type"] = "user"
        return Response(response)

@method_decorator(gzip_page, name="dispatch")
class Dealer_LoginAPI(APIView):
    def post(self, request):
        serializer = DealerLogInSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {
                    "msg": "Invaild email or password",
                    "data": serializer.errors,
                }
            )
        email = serializer.data["email"]
        password = serializer.data["password"]

        user = get_if_exists(User, email=email)

        if not user or not user.check_password(password) or user.is_dealer is False:
            return Response({"msg": "Invaild email or password"})

        if user.is_verified is False:
            HandleEmail(user, "update").start()
            return Response({"status": True, "email": serializer.data["email"]})

        update_last_login(None, user)
        response = Response()
        tokens = get_tokens(user, "gas_dealer")
        if request.data["platform"] == "web":
            response.data = {"access": tokens["access"]}
            response.set_cookie(
                key="refresh",
                value=tokens["refresh"],
                httponly=True,
                samesite="None",
                secure=True,  # Use True in production with HTTPS
            )
        else:
            response.data = tokens
        return response


@method_decorator(gzip_page, name="dispatch")
class GasDealerViewAPI(APIView):
    def get(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            user = User.objects.get(id=payload["id"])
            gas_dealer = Gas_Dealer.objects.get(user=user)
            serializer = GasDealerSerializer(gas_dealer)

            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 200,
                            "data": serializer.data,
                        }
                    )
                )
            )
        except Exception:
            return Response({"msg": "Unauthenticated"})


@method_decorator(gzip_page, name="dispatch")
class GetGasDealerAPI(APIView):
    def get(self, request):
        try:
            gas_dealer = Gas_Dealer.objects.get(id=request.query_params["id"])
            cylinder_price = Cylinder_Price.objects.filter(gas_dealer=gas_dealer)
            if not cylinder_price:
                raise Exception
            fee = Delivery_Fee.objects.get(gas_dealer=gas_dealer)
            serializer = GasDealerSerializer(gas_dealer)
            serializer2 = Cylinder_Price_Serializer(cylinder_price, many=True)
            serializer3 = Delivery_Fee_Serializer(fee)

            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 200,
                            "data": serializer.data,
                            "data2": serializer2.data,
                            "data3": serializer3.data,
                        }
                    )
                )
            )
        except Exception:
            return Response(encrypt(json.dumps({"msg": "Dealer is unavailable"})))


@method_decorator(gzip_page, name="dispatch")
class Update_GasDealer_details(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            gas_dealer = Gas_Dealer.objects.get(user=payload["id"])

            if not gas_dealer:
                return Response(encrypt(json.dumps({})))

            # gas_dealer.selling = request.data.get('selling', gas_dealer.selling)
            gas_dealer.open = request.data.get("open", gas_dealer.open)
            gas_dealer.save()

            serializer = GasDealerSerializer(gas_dealer)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception as e:
            print(e)
