import pytest

from account.tests.conftest import *


def test_stuff(test_user_one):
    assert test_user_one.username == "test"
