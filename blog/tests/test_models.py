import faker
import pytest

from pytest_factoryboy import register
from faker import Factory as FakerFactory

from osonwa.assert_helpers import (
    assert_equal,
    assert_false,
    assert_isinstance,
    assert_not_equal,
    assert_true,
)


faker = FakerFactory.create()


def test_post_creation(db, post_a):
    assert post_a


# def test_post_noauthor(db, post_b):
#     assert post_b


# def test_post_image(db, post_c):
#     assert post_c


# @pytest.mark.skip
# def test_postcreation_signals():
#     pass
