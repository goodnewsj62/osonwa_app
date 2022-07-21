import json
from typing import Sequence, Union

from celery import group, shared_task

from articles_feed.models import ArticleFeed
from articles_feed.scrappers_strategies import (
    CssTrickStrategy,
    DigitalOceanStrategy,
    FreeCodeCampStrategy,
    GitBlogStrategy,
    MediumStrategy,
    SyncFusionStrategy,
)
from osonwa.helpers import (
    ProcessMarkUp,
    generate_b64_uuid_string,
    process_entries,
    save_feed,
    vendor_fromurl,
)
from news.models import RawFeed
from osonwa.tasks import fetch_rss_entries, make_request
from osonwa.constants import (
    SCRAPE_URLS,
    agile_urls_tuple,
    cybersecurity_urls_namedtuple,
    vr_ar_urls_namedtuple,
    webdev_urls_namedtuple,
    gamedev_urls_namedtuple,
    printing3d_urls_namedtuple,
)


def scrape_websites():
    chord = group(make_request.s(url) for url in SCRAPE_URLS) | extract_info.s()
    chord()


@shared_task(queue="cpu")
def extract_info(list_of_tuples: Sequence[Union[str, str]]):
    scrape_strategies = {
        "digitalocean": DigitalOceanStrategy,
        "css-tricks": CssTrickStrategy,
        "medium": MediumStrategy,
        "freecodecamp": FreeCodeCampStrategy,
        "syncfusion": SyncFusionStrategy,
        "about.gitlab": GitBlogStrategy,
    }

    for html_str, url in list_of_tuples:
        vendor = vendor_fromurl(url)
        process_markup = ProcessMarkUp(html_str)
        soup = process_markup.get_bsmarkup()
        site_icon = process_markup.get_icon()
        strategy = scrape_strategies[vendor](soup)
        result_dict = strategy.handle(save_article=lambda **kwargs: print(kwargs))
        id_ = generate_b64_uuid_string()

        ArticleFeed.objects.create(
            hash_id=id_,
            guid=id_,
            title=result_dict.get("title"),
            description=process_markup.__class__(
                result_dict.get("summary")
            ).extract_text(),
            link=result_dict.get("link"),
            date_published=result_dict.get("date"),
            image_url=result_dict.get("image_url"),
            logo_url=site_icon,
            website=vendor,
            scope="web development",
        )


def fetch_from_urls():
    scoped_tuples = [
        agile_urls_tuple,
        cybersecurity_urls_namedtuple,
        vr_ar_urls_namedtuple,
        webdev_urls_namedtuple,
        gamedev_urls_namedtuple,
        printing3d_urls_namedtuple,
    ]

    for tuple_ in scoped_tuples:
        fetch_rss(tuple_.scope, tuple_.urls)


def fetch_rss(scope, urls):
    group_ = group(
        (fetch_rss_entries.s(url, scope) | process_articles_entries_and_save.s())
        for url in urls
    )
    group_()


@shared_task(queue="cpu")
def process_articles_entries_and_save(data: dict):
    # TODO: bad code repitition of those in news
    rawfeed_dump_instance = RawFeed.objects.get(id=data.pop("raw_id"))
    entries = json.loads(rawfeed_dump_instance.string_blob)
    data.update({"entries": entries})
    process_entries(data, save_feed(ArticleFeed))
    rawfeed_dump_instance.delete()
