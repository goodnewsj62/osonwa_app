from random import choice, choices
import string

import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError

from account.models import SocialAccount, User
from osonwa.helpers import assert_equals, assert_false, assert_true


def generate_random_char(length=10):
    return "".join(choices(string.ascii_lowercase, k=length))


def test_user_creation(test_user_one):
    assert_equals(test_user_one.username, "testuser")


def test_duplicate_username(test_user_two, create_user_object):
    with pytest.raises(IntegrityError):
        create_user_object(
            username="kelz",
            password="password",
            email="kele@gmail.com",
            first_name="boo",
            last_name="bae",
        )


def test_duplicate_email(test_user_one, create_user_object):
    with pytest.raises(IntegrityError):
        create_user_object(
            username="testu",
            password="password",
            email="testuser@gmail.com",
            first_name="boo",
            last_name="bae",
        )


def test_invalid_email(db):
    user = User(
        username="testu",
        password="password",
        email="testusergmail.com",
        first_name="boo",
        last_name="bae",
    )

    with pytest.raises(ValidationError):
        user.full_clean()


def test_null_first_name(create_user_object):
    with pytest.raises(IntegrityError):
        create_user_object(
            username="testu",
            password="password",
            email="testuser@gmail.com",
            first_name=None,
            last_name="bae",
        )


def test_null_last_name(create_user_object):
    with pytest.raises(IntegrityError):
        create_user_object(
            username="testu",
            password="password",
            email="testuser@gmail.com",
            first_name="boo",
            last_name=None,
        )


def test_auto_profile_creation(test_user_one):
    assert_true(test_user_one.profile.user.username)


def test_notification(create_notification, test_user_one, test_user_two):
    assert_equals(create_notification.owner, test_user_one)
    assert_equals(create_notification.action_by, test_user_two)


def test_social_accounts(db, test_user_one):
    fake_str_id = generate_random_char()

    social_account = SocialAccount.objects.create(
        social_id=fake_str_id,
        user=test_user_one,
        provider=choice(
            [
                "github",
                "twitter",
                "apple",
                "linkedin",
                "goolge",
            ]
        ),
    )

    assert_equals(social_account.user, test_user_one)


def test_invalid_provider(db, test_user_one):
    fake_str_id = generate_random_char()

    with pytest.raises(ValidationError):
        social_account = SocialAccount(
            social_id=fake_str_id, user=test_user_one, provider="kiev"
        )
        social_account.full_clean()


def test_social_empty_user(db):
    fake_str_id = generate_random_char()

    with pytest.raises(IntegrityError):
        social_account = SocialAccount.objects.create(
            social_id=fake_str_id, user=None, provider="apple"
        )


def test_notification_is_read_false(db, create_notification):
    assert create_notification.is_read == False


def test_notification_empty_owner(db, create_notification):
    create_notification.owner = None
    with pytest.raises(IntegrityError):
        create_notification.save()
