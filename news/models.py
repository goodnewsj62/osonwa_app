from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from osonwa.general_models import DumpDB, Feed, UserFeedGroup, UserReaction, Tag
from core.models import Liked, Saved, Comment

# Create your models here.


class NewsFeed(Feed):
    likes = GenericRelation(Liked, related_query_name="news")
    saved = GenericRelation(Saved, related_query_name="news")
    comments = GenericRelation(Comment, related_query_name="news")

    class Meta:
        verbose_name = "news feed"
        verbose_name_plural = "news feeds"
        ordering = [
            "-date_published",
        ]


class NewsReaction(UserReaction):
    post = models.ForeignKey("news.NewsFeed", on_delete=models.CASCADE)


class CollaborativeNewsFeedGroup(UserFeedGroup):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="collab_news_groups",
        related_query_name="collab_news_groups",
    )

    class Meta:
        pass


class CollabBasedRecommendedNewsFeed(models.Model):
    group = models.OneToOneField(
        "news.CollaborativeNewsFeedGroup", on_delete=models.CASCADE
    )
    feeds = models.ManyToManyField(
        "news.NewsFeed",
        related_name="collaborative_recommendations",
        related_query_name="collaborative_recommendations",
    )

    class Meta:
        pass


class ContentNewsFeedGroups(UserFeedGroup):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="content_news_groups",
        related_query_name="content_news_groups",
    )

    class Meta:
        pass


class ContentBasedRecommendedNewsFeed(models.Model):
    group = models.OneToOneField("news.ContentNewsFeedGroups", on_delete=models.CASCADE)
    feeds = models.ManyToManyField(
        "news.NewsFeed",
        related_name="content_recommendations",
        related_query_name="content_recommendations",
    )

    class Meta:
        pass


class RawFeed(DumpDB):
    pass


class NewsTag(Tag):
    posts = models.ManyToManyField(
        "news.NewsFeed", related_name="tags", related_query_name="tag"
    )
