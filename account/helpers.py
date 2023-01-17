from osonwa.helpers import create_random_word
from django.contrib.auth import get_user_model
from account.models import SocialAccount

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
