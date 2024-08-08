from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    LogInSerializer,
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
from functions.encryption import auth_decoder, auth_encoder, encrypt
from functions.CustomQuery import get_if_exists
from external_api.paystack import create_subaccount, update_subaccount
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from dotenv import load_dotenv
import os
import jwt
import json
import datetime

load_dotenv()
JWT_KEY = os.getenv("JWT_KEY")


@method_decorator(gzip_page, name="dispatch")
class SignUpAPI(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                user = User.objects.get(email=serializer.data["email"])

                payload = {
                    "id": user.id,
                    "type": "verification",
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=15),
                    "iat": datetime.datetime.utcnow(),
                }
                token = auth_encoder(payload)
                HandleEmail(user, "create").start()

                return Response(
                    encrypt(
                        json.dumps(
                            {
                                "status": 200,
                                "message": "User successfully registered check email",
                                "data": serializer.data,
                                "token": token,
                            }
                        )
                    )
                )

            return Response(
                encrypt(
                    json.dumps(
                        {
                            "status": 400,
                            "message": "Something went wrong",
                            "data": serializer.errors,
                        }
                    )
                )
            )

        except Exception as e:
            print(e)
            return Response(encrypt(json.dumps({"status": 400})))


# CHECK IF ACCOUNT IS USER OR GAS DEALER
@method_decorator(gzip_page, name="dispatch")
class AccountViewAPI(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))

            if (
                payload["account_type"] == "user"
                or payload["account_type"] == "gas_dealer"
            ):
                return Response(
                    {
                        "status": 200,
                        "account_type": payload["account_type"],
                    }
                )
            else:
                return Response({"status": 400, "message": "Unauthenticated"})
        except Exception:
            return Response({"status": 400, "message": "Unauthenticated"})


# CHECK IF ACCOUNT IS USER OR GAS DEALER


# USER
@method_decorator(gzip_page, name="dispatch")
class LoginAPI(APIView):
    def error_res(self):
        return Response({"status": 400, "message": "Invaild email or password"})

    def post(self, request):
        try:
            serializer = LogInSerializer(data=request.data)

            if serializer.is_valid():
                email = serializer.data["email"].lower()
                password = serializer.data["password"]

                try:
                    user = User.objects.get(email=email)
                except ObjectDoesNotExist:
                    return self.error_res()

                if not user.check_password(password) or user.is_dealer is True:
                    return self.error_res()

                if user.is_verified is False:
                    payload = {
                        "id": user.id,
                        "type": "verification",
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=15),
                        "iat": datetime.datetime.utcnow(),
                    }
                    token = auth_encoder(payload)
                    return Response({"status": 201, "token": token})

                update_last_login(None, user)
                payload = {
                    "id": user.id,
                    "account_type": "user",
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=15),
                    "iat": datetime.datetime.utcnow(),
                }
                token = auth_encoder(payload)
                return Response(
                    {
                        "status": 200,
                        "token": token,
                    }
                )
            else:
                return self.error_res()
        except Exception:
            return Response(
                {"status": 400, "message": "Something went wrong, try again later"}
            )


# @method_decorator(gzip_page, name='dispatch')
# class ConnectEmailAPI(APIView):
#     def post(self, request):
#         try:
#             try:
#                 user = User.objects.get(usernames=request.data['username'])
#             except ObjectDoesNotExist:
#                 return Response({
#                     'status': 400,
#                     'message':'Invaild user',
#                 })
#             try:
#                 user = User.objects.get(email=request.data['email'])
#                 if user.verified_email is True or user.is_dealer:
#                     return Response({
#                         "status": 400,
#                         "msg": "Email already exists"
#                     })
#             except ObjectDoesNotExist:
#                 user.email = request.data['email']
#                 user.save()
#                 token = get_if_exists(Token, user=user)
#                 def run(action):
#                     HandleEmail(user, action).start()
#                 if token:
#                     run("update")
#                 else:
#                     run("create")
#             return Response({
#                 'status': 200
#             })
#         except Exception:
#             return Response({
#                 "status": 400
#             })

# @method_decorator(gzip_page, name='dispatch')
# class ChangePasswordAPI(APIView):
#     def post(self, request):
#         try:
#             try:
#                 user = User.objects.get(usernames=request.data['username'])
#             except ObjectDoesNotExist:
#                 return Response({
#                     'status': 400,
#                     'message':'Invaild user',
#                 })

#             if user.is_verified is True:
#                 return Response({
#                     'status': 500,
#                     'message':'Already verified',
#                 })
#             if user.check_password(request.data['password']):
#                 return Response({
#                     'status': 400,
#                     'message':'Cannot use this password.',
#                 })
#             user.set_password(request.data['password'])
#             user.is_verified = True
#             user.save()
#             return Response({
#                 'status': 200,
#                 'message':'Password successfully changed',
#             })
#         except Exception:
#             return Response({
#                 "status": 400,
#                 "message": "Something went wrong",
#             })


@method_decorator(gzip_page, name="dispatch")
class ForgotPasswordAPI(APIView):
    def post(self, request):
        try:
            user = User.objects.get(email=request.data["email"])
            HandleEmail(user, "update").start()
            payload = {
                "id": user.id,
                "type": "verification",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=15),
                "iat": datetime.datetime.utcnow(),
            }
            token = auth_encoder(payload)
            return Response({"status": 200, "token": token})
        except ObjectDoesNotExist:
            return Response({"status": 400, "msg": "Invalid email"})


@method_decorator(gzip_page, name="dispatch")
class VerifyOtpChangePasswordAPI(APIView):
    def post(self, request):
        payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
        if request.data["p"] != request.data["p2"]:
            return Response({"status": 400, "msg": "Password does not match"})
        try:
            user = User.objects.get(id=payload["id"])
        except ObjectDoesNotExist:
            return Response({"status": 400, "msg": "error"})
        token = Token.objects.get(user=user)
        if int(token.otp) == int(request.data["otp"]):
            user.set_password(request.data["p"])
            user.is_verified = True
            user.save()
            return Response(
                {
                    "status": 200,
                }
            )
        else:
            return Response({"status": 400, "msg": "Invalid otp"})


@method_decorator(gzip_page, name="dispatch")
class UserViewAPI(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            user = User.objects.get(id=payload["id"])
            serializer = UserSerializer(user)
            encrypted_data = encrypt(json.dumps(serializer.data))

            return Response(
                {
                    "status": 200,
                    "data": encrypted_data,
                }
            )
        except Exception:
            return Response({"status": 400, "message": "Unauthenticated"})


@method_decorator(gzip_page, name="dispatch")
class UpdateUserAPI(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            user = User.objects.get(id=payload["id"])
            if not user:
                return Response({"status": 400, "message": "Invalid user"})

            # user_email = get_if_exists(User,
            #     email=request.data['email'])

            # if user_email and user_email.id != user.id:
            #     return Response({
            #         'status': 400,
            #         'message': 'Email already exists'
            #     })

            # user.email = request.data.get('email', user.email)
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
                            "status": 200,
                            "data": serializer.data,
                        }
                    )
                )
            )
        except Exception as e:
            print(e)
            return Response(
                encrypt(json.dumps({"status": 400, "message": "Unauthenticated"}))
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
                        "status": 400,
                        "message": "Email already exists",
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
                        "status": 400,
                        "message": "Company name already exists",
                    }
                )

        gas_dealer = get_if_exists(Gas_Dealer, phonenumber=request.data["phonenumber"])

        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response(
                    {
                        "status": 400,
                        "message": "Phonenumber already exists",
                    }
                )

        gas_dealer = get_if_exists(
            Gas_Dealer, account_number=request.data["account_number"]
        )

        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response(
                    {
                        "status": 400,
                        "message": "Account Number already exists",
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
                "status": 400,
                "message": "Something went wrong",
            }
        )


@method_decorator(gzip_page, name="dispatch")
class Verify_Otp(APIView):
    def post(self, request):
        payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
        user = get_if_exists(User, id=payload["id"])
        if not user or user.is_verified is True:
            return Response({"status": 400, "message": "Invaild email"})

        token = get_if_exists(Token, user=user)
        if not token:
            return Response({"status": 400, "message": "Invaild email"})

        if token.otp != request.data["otp"]:
            return Response({"status": 400, "message": "Invaild otp"})

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
class Resend_Otp(APIView):
    def post(self, request):
        payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
        user = User.objects.get(id=payload["id"])

        HandleEmail(user, "update").start()
        return Response(
            {
                "status": 200,
            }
        )


@method_decorator(gzip_page, name="dispatch")
class Dealer_LoginAPI(APIView):
    def post(self, request):
        try:
            serializer = DealerLogInSerializer(data=request.data)

            if serializer.is_valid():
                email = serializer.data["email"]
                password = serializer.data["password"]

                try:
                    user = User.objects.get(email=email)
                except ObjectDoesNotExist:
                    return Response(
                        {"status": 400, "message": "Invaild email or password"}
                    )

                if not user.check_password(password) or user.is_dealer is False:
                    return Response(
                        {"status": 400, "message": "Invaild email or password"}
                    )

                if user.is_verified is False:
                    HandleEmail(user, "update").start()
                    return Response({"status": True, "email": serializer.data["email"]})

                update_last_login(None, user)

                payload = {
                    "id": user.id,
                    "account_type": "gas_dealer",
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=15),
                    "iat": datetime.datetime.utcnow(),
                }
                token = jwt.encode(payload, key=JWT_KEY, algorithm="HS256")
                encrypt_token = encrypt(token)

                return Response(
                    {
                        "status": 200,
                        "message": "Login successful",
                        "token": encrypt_token,
                    }
                )
            else:
                return Response(
                    {
                        "status": 400,
                        "message": "Invaild email or password",
                        "data": serializer.errors,
                    }
                )
        except Exception:
            return Response(
                {"status": 400, "message": "Something went wrong, try again later"}
            )


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
            return Response({"status": 400, "message": "Unauthenticated"})


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
            return Response(
                encrypt(json.dumps({"status": 400, "message": "Dealer is unavailable"}))
            )


@method_decorator(gzip_page, name="dispatch")
class Update_GasDealer_details(APIView):
    def post(self, request):
        try:
            payload = auth_decoder(request.META.get("HTTP_AUTHORIZATION"))
            gas_dealer = Gas_Dealer.objects.get(user=payload["id"])

            if not gas_dealer:
                return Response(
                    encrypt(
                        json.dumps(
                            {
                                "status": 400,
                            }
                        )
                    )
                )

            # gas_dealer.selling = request.data.get('selling', gas_dealer.selling)
            gas_dealer.open = request.data.get("open", gas_dealer.open)
            gas_dealer.save()

            serializer = GasDealerSerializer(gas_dealer)

            return Response(
                encrypt(json.dumps({"status": 200, "data": serializer.data}))
            )
        except Exception as e:
            print(e)
