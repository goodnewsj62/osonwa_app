import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osonwa.settings")

app = Celery("osonwa")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


# from news.tasks import fetch_news_rss
# from news.models import NewsFeed
