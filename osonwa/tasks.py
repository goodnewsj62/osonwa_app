from celery import shared_task
from osonwa.helpers import FeedParserWrapper
import requests


@shared_task(queue="cpu")
def fetch_rss_entries(url, scope=None):
    entries = FeedParserWrapper(url).fetch_data_entries()
    return {"entries": entries, "scope": scope, "url": url}


@shared_task(queue="greenqueue")
def make_request(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        response = requests.request(method="get", url=url, headers=headers)
    except ConnectionError:
        # TODO: log to console
        return

    if response.status_code == 200:
        return str(response.content), url
