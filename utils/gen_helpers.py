import os
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
        result = jwt.decode(token, secret, algorithm="HS256")
        return True, result
    except Exception as e:
        return False, {}
