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
def test_user_two(create_user_object):
    param = {"first_name": "kelz", "last_name": "manny"}

    return create_user_object(
        email="kelz@gmail.com", username="kelz", password="password", **param
    )


@pytest.fixture
def create_notification(db, test_user_one, test_user_two):
    return Notification.objects.create(
        owner=test_user_one,
        action_by=test_user_two,
        action="react",
        post_content="test content",
        post_url="https://osonwa.com/blogs/username/idkoprt",
    )


def assert_true(expr):
    if expr:
        assert True
    else:
        assert False


def assert_false(expr):
    if not expr:
        assert True
    else:
        assert False


def assert_equals(input_a, input_b):
    assert input_a == input_b
