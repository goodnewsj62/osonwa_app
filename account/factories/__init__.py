import random

import factory
from django.conf import settings


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "account.User"

    username = factory.Faker("user_name")
    password = "password"
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "account.Notification"

    owner = factory.SubFactory(UserFactory)
    action_by = factory.SubFactory(UserFactory)
    post_content = factory.Faker("text")
    post_url = "https://osonwa.com/foo"
    backend_url = "https://osonwa.com/hey"
    action = random.choices(
        [
            "comment",
            "react",
            "recommendation",
        ],
        k=1,
    )[0]


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "account.Profile"

    user = factory.SubFactory(UserFactory)
    image = factory.django.ImageField(
        from_path=settings.BASE_DIR / "test_media" / "wallpaper.jpg"
    )


class SocialAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "account.SocialAccount"

    social_id = factory.Faker("uuid4")
    provider = random.choices(
        [
            "github",
            "twitter",
            "apple",
            "linkedin",
            "goolge",
        ],
        k=1,
    )[0]
    user = factory.SubFactory(UserFactory)
