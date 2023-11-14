from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from orders.models import Gas_orders
from accounts.models import User, Gas_Dealer, Cylinder_Price, Delivery_Fee
from functions.encryption import jwt_decoder
from external_api.paystack import initialize_payment
from django.conf import settings

# Create your views here.


class PaymentAPI(APIView):
    def post(self, request):
        payload = jwt_decoder(request.META.get('HTTP_AUTHORIZATION'))
        cylinder = request.data['cylinder']
        dealer = request.data['dealer']
        callback_url = request.data['callback_url']

        user = User.objects.get(id=payload['id'])

        if (not user.email or
            len(user.email) == 0 or
            len(user.first_name) == 0 or
            len(user.last_name) == 0 or
            len(user.address) == 0 or
            len(user.phonenumber_ordering) == 0 or
                len(user.state) == 0):

            return Response({
                'status': 400,
                'message': 'Please complete your profile details to complete order.'
            })

        cylinder_price = Cylinder_Price.objects.get(
            gas_dealer=dealer, cylinder=cylinder)

        if not cylinder_price:
            return Response({
                'status': 400,
                'message': 'Gas Dealer is inactive.'
            })

        gas_dealer = Gas_Dealer.objects.get(id=dealer)

        if (gas_dealer.open is False
                or gas_dealer.selling is False):
            return Response({
                'status': 400,
                'message': 'Gas Dealer is inactive.'
            })

        fee = Delivery_Fee.objects.filter(gas_dealer=dealer).first()
        if not fee:
            return Response({
                'status': 400,
                'message': 'Gas Dealer is inactive.'
            })

        try:
            payment = initialize_payment(str(user.email),
                                         int(cylinder_price.price),
                                         int(fee.price),
                                         str(gas_dealer.subaccount_code),
                                         str(callback_url),
                                         str(cylinder),
                                         str(cylinder_price.gas_dealer))

            if (payment['status'] is True):
                payment_object = Payment.objects.filter(
                    reference=payment['data']['reference']).first()

                if not payment_object:
                    Payment.objects.create(user=user,
                                           gas_dealer=cylinder_price.gas_dealer,
                                           payment_for=cylinder_price,
                                           delivery=fee.price,
                                           reference=payment['data']['reference'])

                return Response({
                    'status': 200,
                    'url': payment['data']['authorization_url']
                })

            else:
                return Response({
                    'status': 400,
                    'message': 'Invalid payment'
                })
        except Exception:
            return Response({
                'status': 400,
                'message': "Error processing payment, try again."
            })

# class PaymentAPI(APIView):
#     def post(self, request):
#         payload = jwt_decoder(request.data['token'])
#         cylinder = request.data['cylinder']
#         dealer = request.data['dealer']
#         callback_url = request.data['callback_url']

#         user = User.objects.get(id=payload['id'])

#         if (not user.email or
#             len(user.email) == 0 or
#             len(user.firstname) == 0 or
#             len(user.lastname) == 0 or
#             len(user.address) == 0 or
#             len(user.phonenumber_ordering) == 0 or
#                 len(user.state) == 0):

#             return Response({
#                 'status': 400,
#                 'message': 'Please complete your profile details to complete order.'
#             })

#         cylinder_price = Cylinder_Price.objects.get(
#             gas_dealer=dealer, cylinder=cylinder)

#         if not cylinder_price:
#             return Response({
#                 'status': 400,
#                 'message': 'Gas Dealer is inactive.'
#             })

#         gas_dealer = Gas_Dealer.objects.get(id=dealer)

#         if (gas_dealer.open is False
#                 or gas_dealer.selling is False):
#             return Response({
#                 'status': 400,
#                 'message': 'Gas Dealer is inactive.'
#             })

#         fee = Delivery_Fee.objects.filter(gas_dealer=dealer).first()
#         if not fee:
#             return Response({
#                 'status': 400,
#                 'message': 'Gas Dealer is inactive.'
#             })

#         try:
#             payment = initialize_payment(str(user.email),
#                                          int(cylinder_price.price),
#                                          int(fee.price),
#                                          str(gas_dealer.subaccount_code),
#                                          str(callback_url),
#                                          str(cylinder),
#                                          str(cylinder_price.gas_dealer))
            
#             if (payment['status'] is True):
#                 payment_object = Payment.objects.filter(
#                     reference=payment['data']['reference']).first()

#                 if not payment_object:
#                     Payment.objects.create(user=user,
#                                            gas_dealer=cylinder_price.gas_dealer,
#                                            payment_for=cylinder_price,
#                                            delivery=fee.price,
#                                            reference=payment['data']['reference'])

#                 return Response({
#                     'status': 200,
#                     'reference': payment['data']['reference'],
#                     'url': payment['data']['authorization_url']
#                 })

#             else:
#                 return Response({
#                     'status': 400,
#                     'message': 'Invalid payment'
#                 })
#         except Exception:
#             return Response({
#                 'status': 400,
#                 'message': "Error processing payment, try again."
#             })

#     def get(self, request):
#         try:
#             reference = request.query_params['reference']
#             response = verify_payment(reference)

#             if (response['status'] is True and response['data']['status'] == "success"):
#                 payment = Payment.objects.filter(reference=reference).first()
#                 payment.paid = True
#                 payment.save()

#                 gas_orders = Gas_orders.objects.filter(
#                     reference=payment.reference).first()

#                 if (gas_orders):
#                     return Response({
#                         'status': 200,
#                         'message': "Payment successful"
#                     })
#                 Gas_orders.objects.create(user=payment.user,
#                                           gas_dealer=payment.gas_dealer,
#                                           cylinder=payment.payment_for.cylinder,
#                                           price=payment.payment_for.price,
#                                           delivery=payment.delivery,
#                                           reference=payment.reference)

#                 gas_dealer = Gas_Dealer.objects.filter(
#                     id=payment.gas_dealer.id).first()
#                 gas_dealer.sold += 1
#                 gas_dealer.save()

#                 return Response({
#                     'status': 200,
#                     'message': "Payment successful"
#                 })
#             if (response['status'] is True and response['data']['status'] == "failed"):
#                 return Response({
#                     'status': 400,
#                     'message': "Payment failed"
#                 })

#             if (response['status'] is True and response['data']['status'] == "abandoned"):
#                 return Response({
#                     'status': 400,
#                     'message': "Payment failed"
#                 })
#         except Exception:
#             return Response({
#                 'status': 400,
#                 'message': "verification error"
#             })


class VerifyPayment_Hook(APIView):
    def post(self, request):
        try:
            ip = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip in settings.PAYSTACK_SAFE_IPS:
                if request.data['event'] == 'charge.success':
                    payment = Payment.objects.get(
                        reference=request.data['data']['reference'])
                    Gas_orders.objects.create(user=payment.user,
                                              gas_dealer=payment.gas_dealer,
                                              cylinder=payment.payment_for.cylinder,
                                              price=payment.payment_for.price,
                                              delivery=payment.delivery,
                                              payment=payment)
                    
                    payment.paid = True
                    payment.save()

                    gas_dealer = Gas_Dealer.objects.get(
                        id=payment.gas_dealer.id)
                    gas_dealer.sold += 1
                    gas_dealer.save()

                    return Response({
                        'status': 200,
                        'message': "successful"
                    })
            else:
                return Response({
                    'status': 403,
                }, status=403)
        except Exception:
            # import traceback
            # traceback_msg = traceback.format_exc()  # Get the traceback message
            # print(traceback_msg)
            return Response({
                'status': 400,
            }, status=400)
