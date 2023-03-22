import requests
import random
from pathlib import Path
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

from blog.models import Post
from news.models import NewsFeed
from articles_feed.models import ArticleFeed

from osonwa.helpers import md5_hex_digest
from ..models import SocialHandlesPosted
from ..helpers import order_by_interactions


class FileDownloadHandler:
    def download_media(self, file_url, size=0):
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Mobile Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Upgrade-Insecure-Requests": "1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        }
        req = requests.get(file_url, headers=headers)

        if not req.status_code in [200]:
            return False, ""

        content_length = req.headers["Content-Length"]
        if content_length and content_length < size:
            return False, ""
        else:
            return True, self.create_file(req.content, file_url)

    def create_file(self, bytes_content, name, unique=True):
        suffix = Path(name).suffix
        name_, file_exists = self.generate_name(name, suffix)
        name = (name_ + suffix) if unique else (name + suffix)
        if unique and file_exists:
            return

        with open(name, "wb") as f:
            f.write(bytes_content)
        return name

    def generate_name(self, name, suffix):
        fname = md5_hex_digest(name, "{}-{}")
        path = settings.BASE_DIR / "media" / "dump"
        Path.mkdir(path, parents=True, mode=666, exist_ok=True)
        return fname, Path(path / (fname + suffix)).exists()


class SocialPost:
    def __init__(self):
        # (id , title,slug, post_id ,media_name, media_url,model_type)
        self.post_info = []

    def get_articles(self):
        qs = self.apply_filter(ArticleFeed.objects)
        qs = self.filter_posted_entities(qs, "article")
        return self.get_quality_image_posts(qs, "article")

    def get_news(self):
        qs = self.apply_filter(NewsFeed.objects)
        qs = self.filter_posted_entities(qs, "news")
        return self.get_quality_image_posts(qs, "news")

    def get_posts(self):
        qs = self.apply_filter(Post.objects, "post")
        qs = self.filter_posted_entities(qs, "post")
        return [
            (
                n.id,
                n.title,
                n.slug_title,
                n.post_id,
                n.cover_image.name.split("/")[-1],
                n.cover_image.url,
                "post",
            )
            for n in qs
        ]

    def apply_filter(self, qs, type_=""):
        two_days_back = timezone.now() - timedelta(days=2)
        qs = qs.filter(date_published__gt=two_days_back)
        if type_ != "post":
            recent_qs = qs.exclude(image_url=None)
        return order_by_interactions(recent_qs)[:10]

    def filter_posted_entities(self, qs, type_):
        results = []
        posted_manager = SocialHandlesPosted.objects
        for entity in qs:
            entity_exists = posted_manager.filter(**{type_: entity}).exists()
            if not entity_exists:
                results.append(entity)

        return results

    def get_quality_image_posts(self, qs, type_):
        result = []
        length = len(qs)
        count = 0
        while count < length:
            entity = qs[count]

            if len(result) > 2:
                break

            small_size_img, img_id = FileDownloadHandler.download_media(
                entity.image_url, 100000
            )

            if not small_size_img:
                info = (
                    entity.id,
                    entity.title,
                    entity.slug_title,
                    None,
                    img_id,
                    entity.image_url,
                    type_,
                )
                result.append(info)

        return result

    def pick_random_three(self, list_):
        length = len(list_)
        choosen_idx = random.sample(list(range(length)), k=min(3, length))
        return [list_[index] for index in choosen_idx]

    def select_qualified_posts(self):
        articles = self.get_articles()
        news = self.get_news()
        posts = self.get_posts()

        self.post_info.extend(self.pick_random_three(articles))
        self.post_info.extend(self.pick_random_three(news))
        self.post_info.extend(self.pick_random_three(posts))

    def qualified_post(self):
        self.select_qualified_posts()
        return self.post_info
