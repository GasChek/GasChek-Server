from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (LogInSerializer,
                          DealerLogInSerializer,
                          UserSerializer,
                          GasDealerSerializer)
from .models import User, Gas_Dealer, Token, Abandoned_Subaccounts
from orders.models import Cylinder_Price, Delivery_Fee
from orders.serializers import (Cylinder_Price_Serializer,
                                Delivery_Fee_Serializer)
from rest_framework_api_key.permissions import HasAPIKey
import jwt, json
import datetime
from django.contrib.auth.models import update_last_login
from functions.emails import HandleEmail
from functions.encryption import jwt_decoder, encrypt
from external_api.paystack import create_subaccount, update_subaccount
import os
from dotenv import load_dotenv
from django.core.exceptions import ObjectDoesNotExist

load_dotenv()
JWT_KEY = os.getenv('JWT_KEY')

permission_classes = [HasAPIKey]

# CHECK IF ACCOUNT IS USER OR GAS DEALER
class AccountViewAPI(APIView):
    def get(self, request):
        try:
            payload = jwt_decoder(request.query_params['token'])

            if (payload['account_type'] == 'user'
                    or payload['account_type'] == 'gas_dealer'):
                return Response({
                    'status': 200,
                    'account_type': payload['account_type'],
                })
            else:
                return Response({
                    'status': 400,
                    'message': 'Unauthenticated'
                })
        except Exception:
            return Response({
                'status': 400,
                'message': 'Unauthenticated'
            })
# CHECK IF ACCOUNT IS USER OR GAS DEALER

# USER
class LoginAPI(APIView):
    def post(self, request):
        try:
            serializer = LogInSerializer(data=request.data)

            if serializer.is_valid():
                username = serializer.data['username']
                password = serializer.data['password']

                try:
                    user = User.objects.get(usernames=username)
                except ObjectDoesNotExist:
                    return Response({
                        'status': 400,
                        'message': 'Invaild username or password'
                    })
                
                if (not user.check_password(password)
                        or user.is_dealer is True or user.is_connected_with_device is False):
                    return Response({
                        'status': 400,
                        'message': 'Invaild username or password'
                    })
                
                if user.is_verified is False:
                    return Response({
                        'status': 201,
                        'message': 'Change password',
                        'username': user.usernames
                    })

                update_last_login(None, user)

                payload = {
                    'id': user.id,
                    'account_type': "user",
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=15),
                    'iat': datetime.datetime.utcnow()
                }
                token = jwt.encode(payload, key=JWT_KEY, algorithm='HS256')
                encrypt_token = encrypt(token)

                return Response({
                    'status': 200,
                    'message': "Login successful",
                    'token': encrypt_token,
                })
            else:
                return Response({
                    'status': 400,
                    'message': 'Invaild email or password',
                    # 'data': serializer.errors
                })
        except Exception:
            return Response({
                'status': 400,
                'message': 'Something went wrong, try again later'
            })


class ChangePasswordAPI(APIView):
    def post(self, request):
        try:
            try:
                user = User.objects.get(usernames=request.data['username'])
            except ObjectDoesNotExist:
                return Response({
                    'status': 400,
                    'message':'Invaild user',
                })

            if user.check_password(request.data['password']):
                return Response({
                    'status': 400,
                    'message':'Cannot use this password.',
                })
            user.set_password(request.data['password'])
            user.is_verified = True
            user.save()
            return Response({
                'status': 200,
                'message':'Password successfully changed',
            })
        except Exception:
            return Response({
                "status": 400,
                "message": "Something went wrong",
            })

class UserViewAPI(APIView):
    def get(self, request):
        try:
            payload = jwt_decoder(request.query_params['token'])
            user = User.objects.get(id=payload['id'])
            serializer = UserSerializer(user)
            encrypted_data = encrypt(json.dumps(serializer.data))

            return Response({
                'status': 200,
                'data': encrypted_data,
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'Unauthenticated'
            })


class UpdateUserAPI(APIView):
    def post(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            user = User.objects.get(id=payload['id'])

            if not user:
                return Response({
                    "status": 400,
                    "message": "Invalid user"
                })

            user_email = User.objects.filter(
                email=request.data['email']).first()

            if user_email and user_email.id != user.id:
                return Response({
                    'status': 400,
                    'message': 'Email already exists'
                })
            
            user.email = request.data.get('email', user.email)
            user.firstname = request.data.get('firstname', user.firstname)
            user.lastname = request.data.get('lastname', user.lastname)
            user.country_code = request.data.get('country_code', user.country_code)
            user.phonenumber_ordering = request.data.get(
                'phonenumber_ordering', user.phonenumber_ordering)
            user.phonenumber_gaschek_device_1 = request.data.get(
                'phonenumber_gaschek_device_1', user.phonenumber_gaschek_device_1)
            user.phonenumber_gaschek_device_2 = request.data.get(
                'phonenumber_gaschek_device_2', user.phonenumber_gaschek_device_2)
            user.phonenumber_gaschek_device_3 = request.data.get(
                'phonenumber_gaschek_device_3', user.phonenumber_gaschek_device_3)
            user.address = request.data.get('address', user.address)
            user.state = request.data.get('state', user.state)

            user.save()

            serializer = UserSerializer(user)
            encrypted_data = encrypt(json.dumps(serializer.data))

            return Response({
                'status': 200,
                'data': encrypted_data,
            })
        except Exception :
            return Response({
                'status': 400,
                'message': 'Unauthenticated'
            })
# USER

# DEALER
class CreateGasDealerAPI(APIView):
    def post(self, request):
        user = User.objects.filter(email=request.data['email']).first()
        
        if user:
            if user.is_verified is True:
                return Response({
                    'status': 400,
                    'message': 'Email already exists',
                })
            else:
                gas_dealer = Gas_Dealer.objects.filter(
                    user=user).first()
                Abandoned_Subaccounts.objects.create(company_name=gas_dealer.company_name,
                                                    subaccount_code=gas_dealer.subaccount_code,
                                                    subaccount_id=gas_dealer.subaccount_id)
                user.delete()
              
        gas_dealer = Gas_Dealer.objects.filter(
            company_name=request.data['company_name']).first()
        
        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response({
                    'status': 400,
                    'message': 'Company name already exists',
                })
        
        gas_dealer = Gas_Dealer.objects.filter(
            phonenumber=request.data['phonenumber']).first()
        
        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response({
                    'status': 400,
                    'message': 'Phonenumber already exists',
                })
        
        gas_dealer = Gas_Dealer.objects.filter(
            account_number=request.data['account_number']).first()
        
        if gas_dealer:
            if gas_dealer.is_verified is True:
                return Response({
                    'status': 400,
                    'message': 'Account Number already exists',
                })

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            abandoned_subaccount = Abandoned_Subaccounts.objects.filter(
                                    company_name=request.data['company_name']).first()

            if abandoned_subaccount:
                response = update_subaccount(abandoned_subaccount.subaccount_code, 
                                            request.data['company_name'], 
                                            request.data['bank'], 
                                            str(request.data['account_number']), 
                                            )
                if response['status'] is True:
                    abandoned_subaccount.delete()
                
            else:
                percentage_charge = 2
                response = create_subaccount(request.data['company_name'], 
                                            request.data['bank'], 
                                            str(request.data['account_number']), 
                                            percentage_charge)

            if response['status'] is True:
                serializer.save()
                response = response['data']
        
                user = User.objects.get(email=serializer.data['email'])
                Gas_Dealer.objects.create(user=user,
                                            company_name=request.data['company_name'],
                                            state=request.data['state'],
                                            phonenumber=request.data['phonenumber'],
                                            address=request.data['address'],
                                            account_number=request.data['account_number'],
                                            longitude=request.data['longitude'],
                                            latitude=request.data['latitude'],
                                            bank_name=response['settlement_bank'],
                                            bank_code=request.data['bank'],
                                            percentage_charge=response['percentage_charge'],
                                            subaccount_code=response['subaccount_code'],
                                            subaccount_id=response['id'],
                                        )
                HandleEmail(user, "create").start()

                return Response({
                    'status': 200,
                    'data': serializer.data['email'],
                })

            else:
                return Response({
                    'status': 500,
                    'response': response
                })
            
        return Response({
            'status': 400,
            'message': 'Something went wrong',
        })


class Verify_Otp(APIView):
    def post(self, request):
        user = User.objects.get(email=request.data['email'])

        if not user or user.is_verified is True:
            return Response({
                'status': 400,
                'message': 'Invaild email'
            })

        token = Token.objects.get(user=user)
        if not token:
            return Response({
                'status': 400,
                'message': 'Invaild email'
            })

        if token.otp != request.data['otp']:
            return Response({
                'status': 400,
                'message': 'Invaild otp'
            })
        gas_dealer = Gas_Dealer.objects.filter(user=user).first()
        user.is_verified = True
        gas_dealer.is_verified = True
        user.save()
        gas_dealer.save()
        return Response({
            'status': 200,
        })


class Resend_Otp(APIView):
    def post(self, request):
        user = User.objects.get(email=request.data['email'])

        HandleEmail(user, "update").start()

        return Response({
            'status': 200,
        })

    
class Dealer_LoginAPI(APIView):
    def post(self, request):
        try:
            serializer = DealerLogInSerializer(data=request.data)

            if serializer.is_valid():
                email = serializer.data['email']
                password = serializer.data['password']

                try:
                    user = User.objects.get(email=email)
                except ObjectDoesNotExist:
                    return Response({
                        'status': 400,
                        'message': 'Invaild email or password'
                    })
                
                if (not user.check_password(password)
                        or user.is_dealer is False):
                    return Response({
                        'status': 400,
                        'message': 'Invaild email or password'
                    })
                
                if user.is_verified is False:
                    HandleEmail(user, "update").start()
                    return Response({
                        'status': True,
                        'email': serializer.data['email']
                    })

                update_last_login(None, user)

                payload = {
                    'id': user.id,
                    'account_type': "gas_dealer",
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=15),
                    'iat': datetime.datetime.utcnow()
                }
                token = jwt.encode(payload, key=JWT_KEY, algorithm='HS256')
                encrypt_token = encrypt(token)

                return Response({
                    'status': 200,
                    'message': "Login successful",
                    'token': encrypt_token,
                })
            else:
                return Response({
                    'status': 400,
                    'message': 'Invaild email or password',
                    'data': serializer.errors
                })
        except Exception:
            return Response({
                'status': 400,
                'message': 'Something went wrong, try again later'
            })


class GasDealerViewAPI(APIView):
    def get(self, request):
        try:
            payload = jwt_decoder(request.query_params['token'])
            user = User.objects.get(id=payload['id'])
            gas_dealer = Gas_Dealer.objects.get(user=user)
            serializer = GasDealerSerializer(gas_dealer)

            return Response({
                'status': 200,
                'data': serializer.data,
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'Unauthenticated'
            })


class GetGasDealerAPI(APIView):
    def get(self, request):
        try:
            gas_dealer = Gas_Dealer.objects.get(id=request.query_params['id'])
            cylinder_price = Cylinder_Price.objects.filter(
                gas_dealer=gas_dealer)
            fee = Delivery_Fee.objects.get(gas_dealer=gas_dealer)

            serializer = GasDealerSerializer(gas_dealer)
            serializer2 = Cylinder_Price_Serializer(cylinder_price, many=True)
            serializer3 = Delivery_Fee_Serializer(fee)

            return Response({
                'status': 200,
                'data': serializer.data,
                'data2': serializer2.data,
                'data3': serializer3.data
            })
        except Exception:
            return Response({
                'status': 400,
                'message': 'Error'
            })


class Update_GasDealer_details(APIView):
    def post(self, request):
        try:
            payload = jwt_decoder(request.data['token'])
            gas_dealer = Gas_Dealer.objects.get(user=payload["id"])

            if not gas_dealer:
                return Response({
                    "status": 400,
                })

            # gas_dealer.selling = request.data.get('selling', gas_dealer.selling)
            gas_dealer.open = request.data.get('open', gas_dealer.open)
            gas_dealer.save()

            serializer = GasDealerSerializer(gas_dealer)

            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception as e:
            print(e)
