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
    md5_hex_digest,
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
    chord = group((make_request.s(url) | extract_info.s()) for url in SCRAPE_URLS)
    chord()


@shared_task(queue="cpu")
def extract_info(dbkey_url_tuple):
    pk, url = dbkey_url_tuple
    scrape_strategies = {
        "digitalocean": DigitalOceanStrategy,
        "css-tricks": CssTrickStrategy,
        "medium": MediumStrategy,
        "freecodecamp": FreeCodeCampStrategy,
        "syncfusion": SyncFusionStrategy,
        "about.gitlab": GitBlogStrategy,
    }
    if pk:  # 0 is returned when execption occur in calling task
        dump_db = RawFeed.objects.get(id=pk)
        process_and_create_article_from_htmlstr(
            dump_db.byte_blob.tobytes(), url, scrape_strategies
        )
        dump_db.delete()


def process_and_create_article_from_htmlstr(html_string, url, scrape_strategies):
    vendor = vendor_fromurl(url)
    process_markup = ProcessMarkUp(html_string)
    soup = process_markup.get_bsmarkup()
    strategy = scrape_strategies[vendor](soup)  # pass soup to class
    create_func = create_article(vendor, process_markup.get_icon())
    strategy.handle(create_func)


def create_article(vendor, site_icon):
    def _create(result_dict):
        id_ = generate_b64_uuid_string()
        hash_id = md5_hex_digest(result_dict.get("title"))
        if result_dict.get("summary"):
            summary = ProcessMarkUp(result_dict.get("summary")).extract_text()
        else:
            summary = None

        if not ArticleFeed.objects.filter(hash_id=hash_id).exists():
            instance = ArticleFeed.objects.create(
                hash_id=hash_id,
                gid=id_,
                title=result_dict.get("title"),
                description=summary,
                link=result_dict.get("link"),
                date_published=result_dict.get("date"),
                image_url=result_dict.get("image_url"),
                logo_url=site_icon
                if site_icon.startswith("http")
                else f"https://{vendor}.com",
                website=vendor,
                scope="web development",
            )

    return _create


def fetch_articles_from_urls():
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
    if data and data.get("raw_id"):
        rawfeed_dump_instance = RawFeed.objects.get(id=data.pop("raw_id"))
        entries = json.loads(rawfeed_dump_instance.string_blob)
        data.update({"entries": entries})
        process_entries(data, save_feed(ArticleFeed))
        rawfeed_dump_instance.delete()
