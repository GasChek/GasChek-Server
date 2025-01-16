from rest_framework.views import APIView
from rest_framework.response import Response
from fcm_django.models import FCMDevice
from accounts.models import User
from accounts.utils.auth_utils import jwt_required
from functions.encryption import encrypt, decrypt
import json
import jwt
import os
from functions.CustomQuery import get_if_exists
from dotenv import load_dotenv

load_dotenv()
JWT_DECODE_KEY = os.getenv("JWT_KEY")
# Create your views here.


class Register_Push_Notification(APIView):
    def post(self, request):
        try:
            payload = jwt.decode(
                decrypt(request.META.get("HTTP_AUTHORIZATION")),
                key=JWT_DECODE_KEY,
                algorithms=["HS256"],
            )
            user = User.objects.get(id=payload["id"])

            fcm = get_if_exists(FCMDevice, registration_id=request.data["reg_id"])
            # this will replace details if the token already exists in the database
            if fcm:
                fcm.name = user.first_name
                fcm.user_id = payload["id"]
                fcm.device_id = request.data["device_id"]
                fcm.save()
            else:
                # this will register new token with user
                FCMDevice.objects.create(
                    name="",
                    user_id=payload["id"],
                    device_id=request.data["device_id"],
                    registration_id=request.data["reg_id"],
                    type=request.data["type"],
                )
            return Response(encrypt(json.dumps({"status": 200})))
        except Exception:
            return Response(encrypt(json.dumps({"status": 400})))
