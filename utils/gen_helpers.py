import os
import base64
from uuid import uuid4

import jwt
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def setattr_if_exists(obj: object, data: dict):
    for field, val in data.items():
        if hasattr(obj, field):
            setattr(obj, field, val)


def get_env_variable(var):
    return os.getenv(var)


def generate_jwt_token(payload: dict, exp):
    secret = os.getenv("SECRET_KEY")
    payload = {**payload, "exp": exp}
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_jwt_token(token):
    try:
        secret = os.getenv("SECRET_KEY")
        result = jwt.decode(token, secret, algorithms=["HS256"])
        return True, result
    except Exception as e:
        print(e)
        return False, {}


def base64_encoded_uuid():
    bs64_str = base64.urlsafe_b64encode(str(uuid4()).encode()).decode("utf-8")
    return bs64_str[:10]
