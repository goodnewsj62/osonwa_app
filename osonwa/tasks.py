import json
from celery import shared_task
from news.models import RawFeed
from osonwa.helpers import FeedParserWrapper
import requests


@shared_task(queue="greenqueue")
def fetch_rss_entries(url, scope=None):
    entries = FeedParserWrapper(url).fetch_data_entries()
    print(f"********ENTRIES COUNT: {len(entries)}")
    instance = RawFeed.objects.create(string_blob=json.dumps(entries))
    return {"raw_id": instance.id, "url": url, "scope": scope}


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
            dump_instance = RawFeed.objects.create(byte_blob=response.content)
            return dump_instance.id, url
    except Exception as e:
        # TODO: log to file
        print("error: ", e)
        return 0, url
