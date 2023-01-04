import os
from google.oauth2 import id_token
from google.auth.transport import requests


CLIENT_ID = os.getenv("G_CLIENT_ID")


class GoogleHelper:
    @staticmethod
    def validate(token):
        try:
            resp = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

            return True, resp
        except ValueError:
            return False, {}
