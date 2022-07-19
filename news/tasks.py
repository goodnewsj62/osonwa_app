from osonwa.tasks import (
    fetch_rss_entries,
)  # this is imported here because of gevent monkey patch

from celery import chain, group, shared_task

from news.models import NewsFeed
from osonwa.helpers import process_entries, save_feed

from osonwa.constants import NEWS_RSS_FEED_URLS


def fetch_news_rss():
    group_ = group(
        (fetch_rss_entries.s(url, "tech news") | process_entries_and_save.s())
        for url in NEWS_RSS_FEED_URLS
    )

    group_()


@shared_task
def process_entries_and_save(fetched_entries: dict):
    process_entries(fetched_entries, save_feed(NewsFeed))
