import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY")
SERVER_ENCRYPTION_KEY = os.getenv("SERVER_ENCRYPTION_KEY")
SERVER_ENCRYPTION_IV_KEY = os.getenv("SERVER_ENCRYPTION_IV_KEY").encode("utf-8")


def encrypt(raw):
    #### AES ECB
    # raw = pad(raw.encode(), 16)
    # cipher = AES.new(SERVER_ENCRYPTION_KEY.encode('utf-8'), AES.MODE_ECB)
    # return base64.b64encode(cipher.encrypt(raw))

    #### AES CBC
    data = pad(raw.encode(), 16)
    cipher = AES.new(
        SERVER_ENCRYPTION_KEY.encode("utf-8"), AES.MODE_CBC, SERVER_ENCRYPTION_IV_KEY
    )
    return base64.b64encode(cipher.encrypt(data)).decode("utf-8", "ignore")


def decrypt(enc):
    # enc = base64.b64decode(enc)
    # cipher = AES.new(SERVER_ENCRYPTION_KEY.encode('utf-8'), AES.MODE_ECB)
    # return unpad(cipher.decrypt(enc), 16)

    enc = base64.b64decode(enc)
    cipher = AES.new(
        SERVER_ENCRYPTION_KEY.encode("utf-8"), AES.MODE_CBC, SERVER_ENCRYPTION_IV_KEY
    )
    return unpad(cipher.decrypt(enc), 16).decode("utf-8", "ignore")


def auth_encoder(payload):
    token = jwt.encode(payload, key=str(ACCESS_SECRET_KEY), algorithm="HS256")
    return encrypt(token)


def auth_decoder(token):
    payload = jwt.decode(decrypt(token), key=ACCESS_SECRET_KEY, algorithms=["HS256"])
    return payload
