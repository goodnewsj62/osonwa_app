from abc import ABC, abstractmethod
import time
from functools import partial
import random
import re


import requests
import bs4


def make_request(url, metthod="get", headers={}):
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Mobile Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        **headers,
    }
    response = requests.request(method=metthod, url=url, headers=headers)
    if response.status_code == 200:
        return response.content
    print(
        f"GET REQUEST PROBLEM:--------------: {response} :---- FROM:{url}"
    )  # stdout for logging
    return None


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


class ScrapingStrategy(ABC):
    """
    scraping could be tedious, different site have different mark up and most website change
    over time which the change could include tags class names
    and id which are what we use when scraping - thats why i did this
    """

    @abstractmethod
    def handle(self, save_article=None):
        """plug algorithm variation here"""


class CssTrickStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self, save_article=None):
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

            save_article(
                link=link, title=title, image_url=image_url, summary=summary, date=date
            )


class DigitalOceanStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self, save_article=None):
        articles = self.soup.find(
            class_=re.compile(r"^IndexListStyles__Styled")
        ).find_all("li")

        for article in articles:
            header = article.find("h3")
            next_siblings = header.next_siblings

            next_siblings = list(next_siblings)
            title = header.get_text()
            link = "https://www.digitalocean.com" + header.find("a").get("href")
            image_url = None
            summary = next_siblings[0].get_text()
            date = next_siblings[-1].find("span").get_text()
            save_article(
                link=link, title=title, image_url=image_url, summary=summary, date=date
            )


class MediumStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self, save_article=None):
        articles = self.soup.find_all("article")
        # helps not to follow sequencial order like a bot
        articles = random.sample(articles, k=len(articles))
        for article in articles:
            link = article.find_all("a", limit=5)
            date = link[3].find("p")
            summary = article.find_all("p")
            # too many p with random class look for the one with most number of words
            summary = filter(lambda x: len(x.get_text()) > 20, summary)

            title = article.find("h2").get_text()
            link = "https://medium.com" + link[-1].get("href")
            date = date.get_text()
            if len(date) > 15:
                # handle bad format data
                continue

            image_url = self.get_image_url(link)

            try:
                summary = list(summary)[0].get_text()
            except IndexError:
                summary = None

            save_article(
                link=link, title=title, image_url=image_url, summary=summary, date=date
            )

    def get_image_url(self, link):
        response = make_request(link)
        # hit at different time interval like human
        time.sleep(random.choice([120, 60, 100, 80]))

        if response:
            soup = bs4.BeautifulSoup(response, "lxml")
            main = soup.find("main")
            images = main.find_all("img", limit=3)
            return images[-1].get("src")
        return None


class FreeCodeCampStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self, save_article=None):
        articles = self.soup.find_all("article")
        for article in articles:
            image_url = article.find("img").get("data-cfsrc")
            title = article.find("h2").get_text().strip()
            link = article.find("h2").a.get("href")
            date = article.find("time").get_text()
            summary = None

            # print("\n\n", title, "\n", image_url, "\n", link, "\n", date)
            save_article(
                link=link, title=title, image_url=image_url, summary=summary, date=date
            )


class SyncFusionStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self, save_article=None):
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

            save_article(
                link=link, title=title, image_url=image_url, summary=summary, date=date
            )


class GitBlogStrategy(ScrapingStrategy):
    def __init__(self, soup) -> None:
        self.soup = soup

    def handle(self, save_article=None):
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

            save_article(
                link=link, title=title, image_url=image_url, summary=summary, date=date
            )
