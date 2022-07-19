from osonwa.tasks import fetch_rss_entries, make_request


from typing import Sequence, Union
import bs4
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
    FeedEntryHelper,
    ProcessMarkUp,
    clean_image_url,
    generate_b64_uuid_string,
    id_fromurl,
    logo_from_web_url,
    vendor_fromurl,
)
from osonwa.constants import SCRAPE_URLS


def scrape_websites():
    chord = group(make_request.s(url) for url in SCRAPE_URLS) | extract_info.s()
    chord()


@shared_task
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

        ArticleFeed.objects.create(
            guid=generate_b64_uuid_string(),
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


def fetch_rss(scope, urls):
    group_ = group(
        fetch_rss_entries.s(url, scope).link(process_articles_entries_and_save.s())
        for url in urls
    )
    group_()


@shared_task
def process_articles_entries_and_save(fetched_entries: dict):
    entries = fetched_entries.get("entries")
    for entry in entries:
        entry_helper_object = FeedEntryHelper(entry)
        parser = ProcessMarkUp

        image_url = clean_image_url(entry_helper_object, parser)
        url = fetched_entries.get("url")
        id_ = entry_helper_object.get_unique_id()
        id_ = id_ if id_ else id_fromurl(url)

        ArticleFeed.objects.create(
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
