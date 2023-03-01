import json
from osonwa.tasks import (
    fetch_rss_entries,
)  # this is imported here because of gevent monkey patch

from celery import chain, chord, group, shared_task

from news.models import NewsFeed, RawFeed, NewsTag
from osonwa.helpers import process_entries, save_feed
from osonwa.constants import NEWS_RSS_FEED_URLS


def fetch_news_rss():
    group_ = group(
        (fetch_rss_entries.s(url, "tech news") | process_entries_and_save.s())
        for url in NEWS_RSS_FEED_URLS
    )

    group_()


@shared_task(queue="cpu")
def process_entries_and_save(data: dict):
    if data and data.get("raw_id"):
        rawfeed_dump_instance = RawFeed.objects.get(id=data.pop("raw_id"))
        entries = json.loads(rawfeed_dump_instance.string_blob)
        data.update({"entries": entries})
        process_entries(data, save_feed(NewsFeed))
        rawfeed_dump_instance.delete()
