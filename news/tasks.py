from osonwa.tasks import (
    fetch_rss_entries,
)  # this is imported here because of gevent monkey patch

from celery import shared_task

from news.models import NewsFeed
from osonwa.helpers import (
    FeedEntryHelper,
    ProcessMarkUp,
    clean_image_url,
    id_fromurl,
    logo_from_web_url,
    vendor_fromurl,
)


@shared_task
def process_rss_feed_and_save(fetched_entries: dict):
    entries = fetched_entries.get("entries")

    for entry in entries:
        entry_helper_object = FeedEntryHelper(entry)
        parser = ProcessMarkUp

        image_url = clean_image_url(entry_helper_object, parser)
        url = fetched_entries.get("url")
        id_ = entry_helper_object.get_unique_id()
        id_ = id_ if id_ else id_fromurl(url)

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
