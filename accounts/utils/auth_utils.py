import jwt
import binascii
import os
from jwt.exceptions import DecodeError
from django.http import JsonResponse
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from functions.encryption import encrypt, decrypt


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

    except (binascii.Error, DecodeError) as e:
        print("Failed to decode JWT due to incorrect padding or other errors:", str(e))
        return None
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def jwt_required(token_type):
    def decorator(view_func):
        def wrapped_view(request, *args, **kwargs):
            if token_type == "refresh" and request.data["platform"] == "web":
                token = request.COOKIES.get("refresh")  # Extract token from cookie
            else:
                token = request.META.get("HTTP_AUTHORIZATION")

            if not token:
                return JsonResponse({"msg": "Invalid auth"}, status=403)

            payload = auth_decoder(token, token_type)
            if payload is None:
                response_data = {"msg": "Invalid auth"}
                response = JsonResponse(response_data, status=403)
                if token_type == "refresh" and request.data["platform"] == "web":
                    response.delete_cookie("refresh")
                return response

            if payload["type"] != token_type:
                return JsonResponse({"msg": "Invalid auth"}, status=403)

            request.payload = payload
            return view_func(request, *args, **kwargs)

        return wrapped_view

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
