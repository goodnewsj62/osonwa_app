import os
from google.oauth2 import id_token
from google.auth.transport import requests
from pyfacebook import FacebookApi
from pytwitter import Api as ApiV2
from twitter import Api

CLIENT_ID = os.getenv("G_CLIENT_ID")


class GoogleHelper:
    @staticmethod
    def verify(token):
        try:
            resp = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            return True, resp
        except ValueError:
            return False, {}


class FacebookHelper:
    @staticmethod
    def verify(token, user_id):
        # pass
        try:
            fb = FacebookApi(access_token=token)
            resp = fb.user.get_info(
                user_id=user_id, fields=["id", "email"], return_json=True
            )
            return True, resp
        except ValueError:
            return False, {}


class TwitterHelper:
    def __init__(self) -> None:
        self.consumer_key = os.getenv("TW_CONSUMER_KEY")
        self.consumer_secret = os.getenv("TW_CONSUMER_SECRET")
        self.api = ApiV2(
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            oauth_flow=True,
        )

    def get_request_token(self):
        return self.api.get_authorize_url()

    def _get_access_token(self, oauth_token, oauth_verifier):
        return self.api.generate_access_token(
            f"https://localhost/?oauth_token={oauth_token}&oauth_verifier={oauth_verifier}"
        )

    def get_user_info(self, oauth_token, oauth_verifier):
        # NOTE: might want to break down the function... doing 2 things
        try:
            resp = self._get_access_token(oauth_token, oauth_verifier)
            api = Api(
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                access_token_key=resp.get("oauth_token"),
                access_token_secret=resp.get("oauth_token_secret"),
            )
            user_info_object = api.VerifyCredentials(include_email=True)

            return True, {
                "social_id": str(user_info_object.id),
                "provider": "twitter",
                "email": user_info_object.email,
            }
        except Exception as e:
            # TODO: log error
            return False, {}
