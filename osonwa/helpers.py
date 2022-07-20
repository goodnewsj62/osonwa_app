__author__ = "goodnews osonwa john"

import hashlib
import uuid
import base64
import re
from functools import lru_cache
from typing import Protocol
from urllib.parse import urlsplit


import feedparser
from datetime import datetime
from time import struct_time, mktime

import bs4
from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image
from io import BytesIO


@lru_cache(maxsize=1000)
def vendor_fromurl(url):
    parsed_url = urlsplit(url)
    netloc = parsed_url.netloc
    netloc = re.sub(r"(www)\.", "", netloc)
    return re.sub(r"\.(com|org|net|blog)", "", netloc)


class MarkupParser(Protocol):
    def get_icon(self):
        pass


@lru_cache(maxsize=1000)
def logo_from_web_url(url: str):
    # caching make sense here that's the reason for the closure
    parsed_url = urlsplit(url)
    import requests

    def logo_url(parser: MarkupParser):
        return parser(
            requests.request(
                method="get",
                url=parsed_url.scheme + "://" + parsed_url.hostname,
                headers={
                    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Mobile Safari/537.36"
                },
            )
        ).get_icon()

    return logo_url


def id_fromurl(url):
    result = re.findall(r"[1-9]+", url)
    if isinstance(result, list):
        return result[0]
    return url[7:] + generate_b64_uuid_string()[:7]


class FeedParserWrapper:
    def __init__(self, url: str) -> None:
        self.url = url
        self.parser = feedparser.parse
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Mobile Safari/537.36"
        }

    def set_headers(self, headers: dict):
        if headers and isinstance(headers, dict):
            self.headers = self.headers.update(headers)

    def fetch_data_entries(self):
        data = self.parser(self.url, request_headers=self.headers)
        return data.entries


class FeedEntryHelper:
    def __init__(self, entry: dict) -> None:
        self.entry = entry

    def get_title(self):
        return self.entry.get("title")

    def get_description(self):
        return self.entry.get("description")

    def get_date_published(self):
        published_date = self.entry.get("published_parsed")
        if not published_date:
            published_date = self.entry.get("updated")
        return self._to_datetime_object(published_date)

    def get_unique_id(self):
        id_ = self.entry.get("guid")
        if not id_:
            return self.entry.get("id")
        else:
            return id_

    def get_entry_url(self):
        return self.entry.get("link")

    def get_image_url(self):
        media_content = self.entry.get("media_content")
        if isinstance(media_content, list):
            return media_content[0].get("url")
        elif isinstance(self.entry.get("content"), list):
            return self.entry.get("content")[0].get("value")

        return self.get_description()

    def _to_datetime_object(self, date_rep):
        if isinstance(date_rep, datetime):
            return date_rep
        elif isinstance(date_rep, struct_time):
            return datetime.fromtimestamp(mktime(date_rep))
        elif isinstance(date_rep, str):
            return datetime.strptime(str, "%Y-%m-%dT%H:%M:%S%z")


class ProcessMarkUp:
    def __init__(self, markup: str) -> None:
        self.soup = bs4.BeautifulSoup(markup, "lxml")

    def extract_text_from_body(self):
        return self.soup.body.get_text()

    def extract_text(self):
        return self.soup.get_text()

    def extract_image(self):
        image_result = self.soup.body.img
        image = image_result.get("src") if image_result else None
        if image and re.findall(r"\.(jpg|png|webp|jpeg)", image):
            return image
        else:  # some rss had image url with invalid image src
            return None

    def get_bsmarkup(self):
        return self.soup

    def get_icon(self):
        head = self.soup.find("head")
        icon_link = head.find("link", rel="icon")
        if icon_link:
            return icon_link.get("href")
        return


def clean_image_url(entry_helper_object, parser):
    image_url_content = entry_helper_object.get_image_url()

    if image_url_content and image_url_content.startswith("http"):
        return image_url_content
    elif image_url_content:
        return parser(image_url_content).extract_image()
    elif entry_helper_object.get_description():
        return parser(entry_helper_object.get_description()).extract_image()
    else:
        return None


def generate_b64_uuid_string():
    return base64.urlsafe_b64encode(str(uuid.uuid4()).encode()).decode("utf-8")


def resizeImage(image, width_size=400, format_: str = "jpeg"):
    file = Image.open(image)
    thumb_io = BytesIO()
    width, height = file.size
    format_ = "jpeg" if format_ == "jpg" else format_
    # keep aspect ratio
    file = file.resize([width_size, int((width_size * height) / width)])
    try:
        file.save(thumb_io, format=format_, quality=70)
    except ValueError:
        file = file.convert("RGB")
        file.save(thumb_io, format=format_, quality=70)

    # reset pointer to starting byte
    thumb_io.seek(0)
    return thumb_io


def inmemory_wrapper(image, default_path: str):
    if image == default_path:
        return image

    format_ = "".join(image.url.split(".")[-1:])
    image_file = resizeImage(image, width_size=500, format_=format_)
    return InMemoryUploadedFile(
        image_file,
        "ImageField",
        f"{image.name}",
        f"image/{format_}",
        image_file.tell(),
        None,
    )


def dictfrom_django_choice_field(dj_choices):
    return {choice[0]: choice[1] for choice in dj_choices}


def md5_hex_digest(text: str):
    if not text:
        text = " "

    md5_hash = hashlib.md5(text.encode())
    return str(md5_hash.hexdigest())


def process_entries(fetched_entries, to_db):
    entries = fetched_entries.get("entries")
    # if not entries:
    #     print("hit am oh")
    #     return

    for entry in entries:
        entry_helper_object = FeedEntryHelper(entry)
        parser = ProcessMarkUp

        image_url = clean_image_url(entry_helper_object, parser)
        url = fetched_entries.get("url")
        id_ = entry_helper_object.get_unique_id()
        id_ = id_ if id_ else id_fromurl(url)

        # creating a digest to know same articles
        str_unique_hex = md5_hex_digest(entry_helper_object.get_title())

        to_db(
            hash_id=str_unique_hex,
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


def save_feed(dbmodel):
    def to_db(**kwargs):
        hash_id_exists = dbmodel.objects.filter(hash_id=kwargs.get("hash_id")).exists()
        gid_exsits = dbmodel.objects.filter(gid=kwargs.get("gid")).exists()

        if not (gid_exsits or hash_id_exists):
            dbmodel.objects.create(**kwargs)

    return to_db
