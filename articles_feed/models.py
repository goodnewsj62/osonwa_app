from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from osonwa.general_models import DumpDB, Feed, UserFeedGroup, UserReaction, Tag
from core.models import Liked, Saved, Comment

# Create your models here.


class ArticleFeed(Feed):
    m_name = models.CharField(max_length=15, null=False, blank=False, default="article")
    likes = GenericRelation(Liked, related_query_name="article")
    saved = GenericRelation(Saved, related_query_name="article")
    comments = GenericRelation(Comment, related_query_name="article")

    class Meta:
        verbose_name_plural = "articles feed"
        ordering = [
            "-date_published",
        ]


class ArticleReaction(UserReaction):
    post = models.ForeignKey("articles_feed.ArticleFeed", on_delete=models.CASCADE)


class ContentArticleFeedGroup(UserFeedGroup):
    # NOTE: topic_rank is the max ever for json field
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="content_article_groups",
        related_query_name="content_article_groups",
    )

    class Meta:
        pass


class ContentBasedRecommendedArticle(models.Model):
    group = models.OneToOneField(
        "articles_feed.ContentArticleFeedGroup", on_delete=models.CASCADE
    )
    feeds = models.ManyToManyField(
        "articles_feed.ArticleFeed",
        related_name="content_recommendations",
        related_query_name="content_recommendations",
    )

    class Meta:
        pass


class CollaborativeArticleFeedGroup(UserFeedGroup):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="collab_article_groups",
        related_query_name="collab_article_groups",
    )


class CollabBasedRecommendedArticle(models.Model):
    group = models.OneToOneField(
        "articles_feed.CollaborativeArticleFeedGroup", on_delete=models.CASCADE
    )
    feeds = models.ManyToManyField(
        "articles_feed.ArticleFeed",
        related_name="collaborative_recommendations",
        related_query_name="collaborative_recommendations",
    )

    class Meta:
        pass


class ArticleTag(Tag):
    posts = models.ManyToManyField(
        "articles_feed.ArticleFeed", related_name="tags", related_query_name="tag"
    )
