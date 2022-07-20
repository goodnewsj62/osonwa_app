from osonwa.tasks import (
    fetch_rss_entries,
)  # this is imported here because of gevent monkey patch

from celery import chain, chord, group, shared_task

from news.models import NewsFeed
from osonwa.helpers import process_entries, save_feed

from osonwa.constants import NEWS_RSS_FEED_URLS


def fetch_news_rss():
    chord_ = chord(
        (fetch_rss_entries.s(url, "tech news") for url in NEWS_RSS_FEED_URLS),
        process_entries_and_save.s(),
    )

    chord_()


@shared_task
def process_entries_and_save(all_entries: dict):
    for fetched_entries in all_entries:
        process_entries(fetched_entries, save_feed(NewsFeed))
