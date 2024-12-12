import jwt
import binascii
import os
from jwt.exceptions import DecodeError
from django.http import JsonResponse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from functions.encryption import encrypt, decrypt
from asgiref.sync import sync_to_async
import json

load_dotenv()

ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY")
VERIFICATION_SECRET_KEY = os.getenv("VERIFICATION_SECRET_KEY")
DEVICE_SECRET_KEY = os.getenv("DEVICE_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def generate_auth_token(user, action, account_type, device_id=None):
    if action == "refresh":
        time = timedelta(days=365)
        key = REFRESH_SECRET_KEY
    elif action == "access":
        time = timedelta(minutes=5)
        key = ACCESS_SECRET_KEY
    elif action == "verification":
        time = timedelta(minutes=1)
        key = VERIFICATION_SECRET_KEY
    elif action == "device":
        time = timedelta(days=365)
        key = DEVICE_SECRET_KEY

    payload = {
        "id": user.id,
        "type": action,
        "exp": datetime.now(timezone.utc) + time,
        "iat": datetime.now(timezone.utc),
    }
    if account_type:
        payload["account_type"] = account_type
    if device_id:
        payload["device_id"] = device_id

    token = jwt.encode(
        payload,
        key=key,
        algorithm=ALGORITHM,
    )
    return encrypt(token)


def auth_decoder(token, action):
    try:
        if action == "refresh":
            key = REFRESH_SECRET_KEY
        elif action == "access":
            key = ACCESS_SECRET_KEY
        elif action == "verification":
            key = VERIFICATION_SECRET_KEY
        elif action == "device":
            key = DEVICE_SECRET_KEY

        payload = jwt.decode(
            decrypt(token),
            key=key,
            algorithms=[ALGORITHM],
        )
        return payload

    except (binascii.Error, DecodeError, ValueError) as e:
        print("Failed to decode JWT due to incorrect padding or other errors:", str(e))
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(token_type, partial=False, async_view=False):
    def decorator(view_func):
        def get_request_data(request):
            if async_view:
                return json.loads(request.body.decode("utf-8"))
            return request.data

        def get_token(request):
            # Determine where to retrieve the token from
            if token_type == "refresh":
                request_data = get_request_data(request)

                if request_data["platform"] == "web":
                    return request.COOKIES.get("refresh")
                return request.META.get("HTTP_AUTHORIZATION")
            return request.META.get("HTTP_AUTHORIZATION")

        def handle_auth(request, token):
            # Allow access without token if partial=True
            if partial and token is None:
                request.payload = None
                return True, None

            # Check if the token is missing
            if not token:
                return False, JsonResponse({"msg": "Invalid auth"}, status=403)

            # Decode the token
            payload = auth_decoder(token, token_type)
            if payload is None:  # Token is invalid or expired
                response = JsonResponse({"msg": "Invalid auth"}, status=403)

                if token_type == "refresh":
                    request_data = get_request_data(request)

                    if request_data["platform"] == "web":
                        response.delete_cookie("refresh")
                    return False, response
                return False, response

            # Check if token type matches
            if payload["type"] != token_type:
                return False, JsonResponse({"msg": "Invalid auth"}, status=403)

            # Attach payload to request
            request.payload = payload
            return True, None

        def sync_wrapped_view(request, *args, **kwargs):
            token = get_token(request)
            is_valid, response = handle_auth(request, token)
            return view_func(request, *args, **kwargs) if is_valid else response

        async def async_wrapped_view(request, *args, **kwargs):
            token = await sync_to_async(get_token)(request)
            is_valid, response = await sync_to_async(handle_auth)(request, token)
            return await view_func(request, *args, **kwargs) if is_valid else response

        return async_wrapped_view if async_view else sync_wrapped_view

    return decorator


def jwt_required_ws(token, token_type):
    if not token:
        return None

    payload = auth_decoder(token, token_type)
    if payload is None or payload["type"] != token_type:
        return None

    return payload


def get_tokens(user, account_type):
    return {
        "access": generate_auth_token(user, "access", account_type),
        "refresh": generate_auth_token(user, "refresh", account_type),
    }
