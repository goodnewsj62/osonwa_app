from io import StringIO
import json
import pytest
from unittest.mock import patch


from articles_feed.tasks import process_articles_entries_and_save
from articles_feed.models import ArticleFeed
from news.models import RawFeed
from osonwa.helpers import process_entries
from osonwa.tasks import fetch_rss_entries
from osonwa.assert_helpers import assert_equal, assert_true


def test_feed_fetch(db):
    with open("/home/goodnews/Documents/work_folder/osonwa/osonwa/mock_feed.json") as b:
        file = StringIO(b.read())

    with patch(
        "osonwa.helpers.FeedParserWrapper.fetch_data_entries",
        return_value=json.loads(file.getvalue()),
    ):
        data = fetch_rss_entries("https://somesites.com")
        process_articles_entries_and_save(data)

    title = "Google apps on Android tablets receive multitasking improvements"
    assert_true(ArticleFeed.objects.filter(title=title).exists())


def test_article_scraper():
    pass


def test_empty_data_on_process_articles_entries(db):
    process_articles_entries_and_save({})
    assert_equal(RawFeed.objects.first(), None)
