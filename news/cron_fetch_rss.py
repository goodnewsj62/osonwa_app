import re
import feedparser
from urllib.parse import urlsplit
from datetime import datetime
from time import struct_time, mktime


def vendor_fromurl(url):
    parsed_url = urlsplit(url)
    netloc = parsed_url.netloc
    netloc = re.sub(r"(www)\.", "", netloc)
    return re.sub(r"\.(com|org|net|blog)", "", netloc)


def id_fromurl(url):
    result = re.findall(r"[1-9]+", url)
    if isinstance(result, list):
        return result[0]
    return url


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
    def __init__(self, entry: dict, markup_parser_class) -> None:
        self.entry = entry
        self.markup_parser_class = markup_parser_class

    def get_title(self):
        return self.entry.get("title")

    def get_description(self):
        description = self.entry.get("description")
        return self._extract_text_from_html(description)

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
        pass

    def _to_datetime_object(self, date_rep):
        if isinstance(date_rep, datetime):
            return date_rep
        elif isinstance(date_rep, struct_time):
            return datetime.fromtimestamp(mktime(date_rep))
        elif isinstance(date_rep, str):
            return datetime.strptime(str, "%Y-%m-%dT%H:%M:%S%z")

    def _extract_text_from_html(self, text):
        return self.markup_parser_class(text).extract_text()


rss_urls = [
    # r"https://www.techspot.com/backend.xml",
    # r"https://appleinsider.com/rss/news/",
    # r"https://thenextweb.com/feed",
    # "https://www.techmeme.com/feed.xml?x=1",
    # r"https://www.theverge.com/rss/index.xml",
    # r"https://www.computerworld.com/index.rss",  #print("-++++++++++++++++++-", entry.media_thumbnail[0].get("url"))
    # r"https://feeds.washingtonpost.com/rss/business/technology",# No image
    # r"https://siliconangle.com/feed",
    # r"https://vulcanpost.com/feed",
    # r"http://feeds.arstechnica.com/arstechnica/technology-lab",
    # r"https://lwn.net/headlines/newrss", # No image
    # # ************************
    # r"https://martinfowler.com/feed.atom", #no image
    # r"https://dev.to/feed",
    # r"https://towardsdatascience.com/feed",
    # "https://pythonistaplanet.com/feed",  try scraping
    # "https://www.geeksforgeeks.org/feed", # no image
    # "https://stackoverflow.blog/feed",
    # "https://towardsthecloud.com/rss.xml", # no image
]
# for url in rss_urls:
#     feed_object = ProcessRssFeed(url)
#     process_markup = ProcessMarkUp
#     feed_entries = feed_object.fetch_data_entries()
#     for entry in feed_entries:
#         print(f"title: {entry.title}", end="\n\n")
#         # # print(f"description: {entry.description}", end="\n\n")
#         print(
#             f"id: { entry.get('guid') if entry.get('guid') else entry.get('id')}",
#             end="\n\n",
#         )
#         print(
#             f'pud_date: {entry.get("published_parsed") if entry.get("published_parsed") else entry.get("updated")}',
#             end="\n\n",
#         )
#         print(f"link: {entry.link}", end="\n\n")
#         content = entry.get("content")
#         print(
#             "--------------------", entry.get("cover_image")
#         )  # towards the cloud template
#         image = process_markup(entry.description).extract_image()
#         if not image and content:
#             image = (
#                 process_markup(content[0].get("value")).extract_image()
#                 if entry.get("content")
#                 else None
#             )

#         print(image)

blog_urls = [
    # "https://css-tricks.com",
    # "https://www.digitalocean.com/community/tutorials",
    # "https://medium.com/tag/programming",
    # "https://medium.com/tag/python",
    # "https://medium.com/tag/go",
    # "https://www.freecodecamp.org/news",
    # "https://www.syncfusion.com/blogs",
    # "https://about.gitlab.com/blog/",
]

# templates = {
#     "digitalocean": DigitalOceanStrategy,
#     "css-tricks": CssTrickStrategy,
#     "medium": MediumStrategy,
#     "freecodecamp": FreeCodeCampStrategy,
#     "syncfusion": SyncFusionStrategy,
#     "about.gitlab": GitBlogStrategy,
# }

# for url in blog_urls:
#     vendor = ProcessRssFeed.vendor_fromurl(url)
#     response = make_request(url)
#     if not response:
#         continue
#     process_markup = ProcessMarkUp(response)
#     soup = process_markup.get_bsmarkup()
#     template = templates[vendor](soup)
#     print(f"ICON---{process_markup.get_icon()}")
#     # new_save = partial(vendor_icon=process_markup.get_icon() )
#     template.handle(save_article=lambda **kwargs: print(kwargs))
