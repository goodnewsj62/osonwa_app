from gevent import monkey

monkey.patch_all()

from celery import shared_task
from osonwa.helpers import FeedParserWrapper


@shared_task
def fetch_rss_entries(url, scope=None):
    entries = FeedParserWrapper(url).fetch_data_entries()
    return {"entries": entries, "scope": scope, "url": url}
