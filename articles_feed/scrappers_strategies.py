from abc import ABC, abstractmethod
import random
import re
from datetime import datetime, timedelta, timezone


class ScrapingStrategy(ABC):
    """
    scraping could be tedious, different site have different mark up and most website change
    over time which the change could include tags class names
    and id which are what we use when scraping - thats why i did this
    """

    @abstractmethod
    def handle(self):
        """plug algorithm variation here"""

    @staticmethod
    @abstractmethod
    def to_native_date(date_str: str):
        pass


class CssTrickStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self):
        article_list = self.soup.find_all("article", class_="article-card")
        for article in article_list:
            if "sponsored" in article.find(class_="author-row").get_text().lower():
                # skip for sponsored post
                continue

            header = article.find("h1") if article.find("h1") else article.find("h2")
            image = article.find("img")
            content = article.find(class_="card-content")

            link = header.find("a").get("href")
            title = re.sub(r"\n", "", header.get_text().strip())
            image_url = image.get("src")
            summary = content.find("p").get_text(), content.find("p")
            date = re.sub(r"\n", "", article.find("time").get_text().strip())

            return dict(
                link=link,
                title=title,
                image_url=image_url,
                summary=summary,  # clean the summary
                date=self.to_native_date(date),
            )

    @staticmethod
    def to_native_date(date_str: str):
        return datetime.strptime(date_str, r"%b %d, %Y")


class DigitalOceanStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self):
        articles = self.soup.find_all("a", class_=re.compile(r"^Tutorial"))

        for article in articles:
            header = article.find("h3")
            next_siblings = header.next_siblings

            next_siblings = list(next_siblings)
            title = header.get_text()
            link = "https://www.digitalocean.com" + article.get("href")
            image_url = None
            summary = None
            date = next_siblings[-1].find("span").get_text()
            return dict(
                link=link,
                title=title,
                image_url=image_url,
                summary=summary,
                date=self.to_native_date(date),
            )

    @staticmethod
    def to_native_date(date_str: str):
        return datetime.strptime(date_str, r"%B %d, %Y")


class MediumStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self):
        articles = self.soup.find_all("article")
        # helps not to follow sequencial order like a bot
        # articles = random.sample(articles, k=len(articles))
        for article in articles:
            link = article.find_all("a", limit=5)
            date = article.find(string=re.compile("ago$"))
            summary = article.find_all("p")
            # too many p with random class look for the one with most number of words
            summary = filter(lambda x: len(x.get_text()) > 20, summary)

            title = article.find("h2").get_text()
            link = "https://medium.com" + link[-1].get("href")
            image_url = article.find("img").get("src")

            try:
                summary = list(summary)[0].get_text()
            except IndexError:
                summary = None

            return dict(
                link=link,
                title=title,
                image_url=image_url,
                summary=summary,
                date=self.to_native_date(date),
            )

    @staticmethod
    def to_native_date(date_str: str):
        search_result = re.search(r"(\d+)\s(.+)\s", date_str)
        num = search_result.groups()[0]
        str_ = search_result.groups()[1]

        if str_.startswith("hour"):
            return datetime.now(tz=timezone.utc) - timedelta(hours=int(num))
        elif str_.startswith("day"):
            return datetime.now(tz=timezone.utc) - timedelta(days=int(num))


class FreeCodeCampStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self):
        articles = self.soup.find_all("article")
        for article in articles:
            image_url = article.find("img").get("data-cfsrc")
            title = article.find("h2").get_text().strip()
            link = article.find("h2").a.get("href")
            date = list(article.find("time").stripped_strings)
            summary = None

            # print("\n\n", title, "\n", image_url, "\n", link, "\n", date)
            return dict(
                link=link,
                title=title,
                image_url=image_url,
                summary=summary,
                date=self.to_native_date(date[0]),
            )

    @staticmethod
    def to_native_date(date_str):
        search_result = re.search(r"(\d+)\s(.+)\s", date_str)
        if search_result:
            num = search_result.groups()[0]
            str_ = search_result.groups()[1]
            return FreeCodeCampStrategy.handle_expected_date_case(num, str_)
        elif re.search(r"([an])\s(.+)\s", date_str):
            search_result = re.search(r"([an])\s(.+)\s", date_str)
            starting_str = search_result.groups()[0]
            how_long_str = search_result.groups()[1]
            return FreeCodeCampStrategy.handle_starting_str_date(
                starting_str, how_long_str
            )
        elif re.search(r"^[Tt].+"):
            return datetime.now(tz=timezone.utc)

    @staticmethod
    def handle_starting_str_date(starting_str, how_long_str):
        if starting_str.endswith("n"):
            # the only correct possible word: an hour ago
            return datetime.now(tz=timezone.utc) - timedelta(hours=1)
        elif starting_str.startswith("a") and how_long_str.startswith("day"):
            return datetime.now(tz=timezone.utc) - timedelta(days=1)
        elif starting_str.startswith("a") and how_long_str.startswith("mon"):
            return datetime.now(tz=timezone.utc) - timedelta(days=30)

    @staticmethod
    def handle_expected_date_case(num, str_):
        if str_.startswith("hour"):
            return datetime.now(tz=timezone.utc) - timedelta(hours=int(num))
        elif str_.startswith("day"):
            return datetime.now(tz=timezone.utc) - timedelta(days=int(num))


class SyncFusionStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self):
        articles = self.soup.find(class_="loop-wrapper").find_all(
            "div", recursive=False
        )
        print(len(articles))
        for article in articles:
            title_div = article.find("h2")
            link_tag = title_div.find("a")
            image_tag = article.find("amp-img")

            title = title_div.get_text()
            link = link_tag.get("href")
            image_url = image_tag.get("src")
            date = article.find(class_="loop-date").parent.get_text()

            try:
                date = re.findall(r".+\s\d+,\s\d{4}", date)[0]
            except IndexError:
                pass
            summary = None

            return dict(
                link=link,
                title=title,
                image_url=image_url,
                summary=summary,
                date=self.to_native_date(date.strip()),
            )

    @staticmethod
    def to_native_date(date_str: str):
        return DigitalOceanStrategy.to_native_date(date_str)


class GitBlogStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self):
        articles = self.soup.find(class_="blog-recent-post-grid").find_all(
            class_="blog-card"
        )
        for article in articles:
            link = article.find("a").get("href")

            title = article.find("h3").get_text()
            date = article.find(class_="blog-card-date").get_text()
            image_url = article.find("img").attrs.get("src")
            summary = article.find("p").get_text()

            link = "https://about.gitlab.com" + link
            image_url = "https://about.gitlab.com" + image_url
            summary = re.sub(r"\n", "", summary)
            title = re.sub(r"\n", "", title)
            date = re.sub(r"\n", "", date)

            return dict(
                link=link,
                title=title,
                image_url=image_url,
                summary=summary,
                date=self.to_native_date(date.strip()),
            )

    @staticmethod
    def to_native_date(date_str: str):
        return CssTrickStrategy.to_native_date(date_str)
