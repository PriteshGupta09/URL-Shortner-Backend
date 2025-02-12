import jwt
from flask import request

SECRET_KEY = "YOUR_SECRET_KEY"

def DecodeJWT():
    token = request.cookies.get('token')
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload['user_id']