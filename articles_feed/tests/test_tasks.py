import os
from io import BytesIO, StringIO
import json
from unittest.mock import patch

from django.conf import settings

from articles_feed.tasks import extract_info, process_articles_entries_and_save
from articles_feed.models import ArticleFeed
from news.models import RawFeed
from osonwa.helpers import process_entries
from osonwa.tasks import fetch_rss_entries, make_request
from osonwa.assert_helpers import assert_equal, assert_true


def test_feed_fetch(db):
    with open(settings.BASE_DIR / "osonwa/mock_feed.json") as b:
        file = StringIO(b.read())

    with patch(
        "osonwa.helpers.FeedParserWrapper.fetch_data_entries",
        return_value=json.loads(file.getvalue()),
    ):
        data = fetch_rss_entries("https://somesites.com")
        process_articles_entries_and_save(data)

    title = "Google apps on Android tablets receive multitasking improvements"
    assert_true(ArticleFeed.objects.filter(title=title).exists())


def test_article_scraper(db):
    with open(settings.BASE_DIR / "articles_feed/scraped_mock.html", "rb") as b:
        file = BytesIO(b"")
        file.content = b.read()
        file.status_code = 200

    with patch("requests.request", return_value=file):
        data = make_request("https://www.freecodecamp.org/news")
        print(data)
        extract_info(data)
        assert_true(ArticleFeed.objects.filter(website="freecodecamp").exists())


def test_empty_data_on_process_articles_entries(db):
    process_articles_entries_and_save({})
    assert_equal(RawFeed.objects.first(), None)
