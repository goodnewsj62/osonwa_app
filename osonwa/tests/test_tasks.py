import pytest
from news.models import RawFeed

from osonwa.tasks import create_dump_based_on_input_type
from osonwa.assert_helpers import assert_equal, assert_true


def test_create_feed_dump_based_on_bytes_input(db):
    byte_string = b"""hey this is in bytes"""
    id_ = create_dump_based_on_input_type(byte_string)

    assert_true(RawFeed.objects.filter(pk=id_).exists())
    assert_equal(RawFeed.objects.get(pk=id_).byte_blob, byte_string)


def test_create_feed_dump_based_on_string_input(db):
    test_string = """hey this is in bytes"""
    id_ = create_dump_based_on_input_type(test_string)

    assert_true(RawFeed.objects.filter(pk=id_).exists())
    assert_equal(RawFeed.objects.get(pk=id_).string_blob, test_string)


def test_create_feed_dump_based_on_invalid_input(db):
    with pytest.raises(UnboundLocalError):
        test_input = {}
        create_dump_based_on_input_type(test_input)


def test_create_feed_dump_with_no_db(db):
    pass
