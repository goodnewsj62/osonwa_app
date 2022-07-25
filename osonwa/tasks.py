import json
import logging

from django.db import OperationalError, DatabaseError
from celery import shared_task


from news.models import RawFeed
from osonwa.helpers import FeedParserWrapper
import requests

logger = logging.getLogger("celery")


@shared_task(queue="greenqueue")
def fetch_rss_entries(url, scope=None):
    entries = FeedParserWrapper(url).fetch_data_entries()
    dump_id = create_feed_dump(json.dumps(entries))
    return {"raw_id": dump_id, "url": url, "scope": scope}


@shared_task(queue="greenqueue")
def make_request(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }

        import time

        time.sleep(1)  # debounce
        response = requests.request(method="get", url=url, headers=headers)
        if response.status_code == 200:
            dump_id = create_feed_dump(response.content)
            return dump_id, url
    except Exception as e:
        logger.exception("make_request exception")
        return 0, url


def create_feed_dump(dump_input):
    try:
        return create_dump_based_on_input_type(dump_input)
    except (OperationalError, DatabaseError, UnboundLocalError) as e:
        logger.exception(f"creating database dump error: {e}")
        return 0


def create_dump_based_on_input_type(dump_input):
    if isinstance(dump_input, str):
        instance = RawFeed.objects.create(string_blob=dump_input)
    elif isinstance(dump_input, bytes):
        instance = RawFeed.objects.create(byte_blob=dump_input)
    return instance.id
