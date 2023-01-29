import pytest
from pytest_factoryboy import register


from account.models import User
from account.factories import (
    UserFactory,
    NotificationFactory,
    ProfileFactory,
    SocialAccountFactory,
)


factories_ = [
    (UserFactory, "user"),
    (NotificationFactory, "notification"),
    (ProfileFactory, "profile"),
    (SocialAccountFactory, "social"),
]


for factory in factories_:
    register(
        factory[0]
    )  # factories needed globally by other factories defining subfactory from them

    register(factory[0], f"{factory[1]}_a")


@pytest.fixture
def create_user_object(db):
    def create_user(email, username, password, **kwargs):
        user = User.objects.create(
            email=email, username=username, password=password, **kwargs
        )
        user.set_password(password)

        return user

    return create_user


@pytest.fixture
def test_user_gen(create_user_object):
    param = {"first_name": "goody", "last_name": "bag"}

    return create_user_object(
        email="testuser@osonwa.com", username="tester2", password="password", **param
    )
