import pytest

from account.models import Notification, User


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
def test_user_one(create_user_object):
    param = {"first_name": "goody", "last_name": "bag"}

    return create_user_object(
        email="testuser@gmail.com", username="testuser", password="password", **param
    )


@pytest.fixture
def create_notification(db):
    Notification.objects.create()
