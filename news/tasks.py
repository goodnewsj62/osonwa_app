from osonwa.tasks import (
    fetch_rss_entries,
)  # this is imported here because of gevent monkey patch

from celery import chain, group, shared_task

from news.models import NewsFeed
from osonwa.helpers import (
    FeedEntryHelper,
    ProcessMarkUp,
    clean_image_url,
    id_fromurl,
    logo_from_web_url,
    vendor_fromurl,
)
from osonwa.constants import NEWS_RSS_FEED_URLS


def fetch_news_rss():
    group_ = group(
        (fetch_rss_entries.s(url, "tech news") | process_entries_and_save.s())
        for url in NEWS_RSS_FEED_URLS
    )

    group_()


@shared_task
def process_entries_and_save(fetched_entries: dict):
    print("-------------------++++++++++++++++++")
    entries = fetched_entries.get("entries")
    for entry in entries:
        entry_helper_object = FeedEntryHelper(entry)
        parser = ProcessMarkUp

        image_url = clean_image_url(entry_helper_object, parser)
        url = fetched_entries.get("url")
        id_ = entry_helper_object.get_unique_id()
        id_ = id_ if id_ else id_fromurl(url)

        print("-------------------++++++++++++++++++:  =====", image_url)
        # TODO: check if the newsfeed already exists here
        NewsFeed.objects.create(
            gid=id_,
            title=entry_helper_object.get_title(),
            description=parser(entry_helper_object.get_description()).extract_text(),
            link=entry_helper_object.get_entry_url(),
            date_published=entry_helper_object.get_date_published(),
            image_url=image_url,
            website=vendor_fromurl(url),
            logo_url=logo_from_web_url(url)(parser),
            scope=fetched_entries.get("scope"),
        )
        print("-------------------++++++++++++++++++")
