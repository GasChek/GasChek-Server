from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from accounts.serializers import UserSerializer
from .seralizers import AdminLogInSerializer
from accounts.models import User
from django.contrib.auth.models import update_last_login
import jwt, datetime
import os
from dotenv import load_dotenv
from functions.encryption import encrypt
from functions.CustomQuery import get_if_exists
from django.core.exceptions import ObjectDoesNotExist

load_dotenv()
JWT_KEY = os.getenv("JWT_KEY")
# Create your views here.


class CreateUserAPI(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "status": 200,
                    "data": serializer.data,
                }
            )

        return Response(
            {
                "status": 400,
                "message": "Something went wrong",
                "data": serializer.errors,
            }
        )


class AdminLoginAPI(APIView):
    def post(self, request):
        try:
            serializer = AdminLogInSerializer(data=request.data)

            if serializer.is_valid():
                email = serializer.data["email"]
                password = serializer.data["password"]

                user = get_if_exists(User, email=email)

                if (
                    not user
                    or not user.check_password(password)
                    or user.is_superuser is False
                ):
                    return Response(
                        {"status": 400, "message": "Invaild email or password"}
                    )

                update_last_login(None, user)

                payload = {
                    "id": user.id,
                    "account_type": "admin",
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(days=5),
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
                        # 'data': serializer.errors
                    }
                )
        except Exception:
            return Response(
                {"status": 400, "message": "Something went wrong, try again later"}
            )


class List_Not_Connected_With_Device_UsersAPI(APIView, LimitOffsetPagination):
    def get(self, request):
        try:
            user = User.objects.filter(
                is_connected_with_device=False, is_dealer=False, is_superuser=False
            ).order_by("id")
            results = self.paginate_queryset(user, request, view=self)
            serializer = UserSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        except Exception:
            return Response(
                {
                    "status": 400,
                }
            )


class Verify_User_Connection_With_DeviceAPI(APIView):
    def post(self, request):
        try:
            user = User.objects.get(id=request.data["id"])
            user.is_connected_with_device = True
            user.save()

            return Response(
                {
                    "status": 200,
                }
            )

        except Exception:
            return Response({"status": 400, "message": "Something went wrong"})


class List_Unverified_UsersAPI(APIView, LimitOffsetPagination):
    def get(self, request):
        try:
            user = User.objects.filter(
                is_connected_with_device=True,
                is_verified=False,
                is_dealer=False,
                is_superuser=False,
            ).order_by("id")
            results = self.paginate_queryset(user, request, view=self)
            serializer = UserSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        except Exception:
            return Response(
                {
                    "status": 400,
                }
            )


class List_Verified_UsersAPI(APIView, LimitOffsetPagination):
    def get(self, request):
        try:
            user = User.objects.filter(
                is_connected_with_device=True,
                is_verified=True,
                is_dealer=False,
                is_superuser=False,
            ).order_by("id")
            results = self.paginate_queryset(user, request, view=self)
            serializer = UserSerializer(results, many=True)
            return self.get_paginated_response(serializer.data)

        except Exception:
            return Response(
                {
                    "status": 400,
                }
            )
