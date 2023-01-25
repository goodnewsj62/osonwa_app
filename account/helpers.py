from collections import OrderedDict

from django.shortcuts import get_object_or_404
from osonwa.helpers import create_random_word
from django.contrib.auth import get_user_model
from account.models import SocialAccount, TokenStore
from utils.gen_helpers import decode_jwt_token

User = get_user_model()


def perform_user_creation(provider, social_id, **kwargs):
    user = User.objects.create(**kwargs)
    random_password = create_random_word(length=9)
    user.set_password(random_password)
    user.save()
    create_social_account(user, social_id, provider)
    return user


def create_social_account(user, social_id, provider):
    return SocialAccount.objects.create(
        social_id=social_id, provider=provider, user=user
    )


def shorten_token(token):
    store_obj = TokenStore.objects.create(token=token)
    return store_obj.identifier


def extract_data_from_token(data):
    resp = OrderedDict()
    store_obj = get_object_or_404(TokenStore, identifier=data.get("token"))
    status, payload = decode_jwt_token(store_obj.token)
    if not status:
        return {}
    resp["email"] = payload.get("email")
    resp["password"] = data.get("password")
    return resp
