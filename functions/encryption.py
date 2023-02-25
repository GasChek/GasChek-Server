import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
JWT_KEY = os.getenv('JWT_KEY')
SERVER_ENCRYPTION_KEY = os.getenv('SERVER_ENCRYPTION_KEY')


def encrypt(raw):
    raw = pad(raw.encode(), 16)
    cipher = AES.new(SERVER_ENCRYPTION_KEY.encode('utf-8'), AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(raw))


def decrypt(enc):
    enc = base64.b64decode(enc)
    cipher = AES.new(SERVER_ENCRYPTION_KEY.encode('utf-8'), AES.MODE_ECB)
    return unpad(cipher.decrypt(enc), 16)


def jwt_decoder(token):
    d_token = decrypt(token).decode("utf-8", "ignore")
    payload = jwt.decode(d_token, key=JWT_KEY, algorithms=['HS256'])
    return payload
