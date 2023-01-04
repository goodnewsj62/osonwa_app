from django.contrib.auth import get_user_model
from account.models import SocialAccount

User = get_user_model()


def perform_user_creation(provider, social_id, **kwargs):
    user = User.objects(**kwargs)
    SocialAccount.objects.create(social_id=social_id, provider=provider, user=user)
    return user
