from django.db import models
from django.conf import settings

from osonwa.general_models import UserFeedGroup

# Create your models here.


class ContentArticleFeedGroup(UserFeedGroup):
    # NOTE: topic_rank is the max ever for json field
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="content_article_groups",
        related_query_name="content_article_groups",
    )

    class Meta:
        pass


class ContentBasedRecommendedArticles(object):
    group = models.OneToOneField()
    feeds = models.ManyToManyField()

    class Meta:
        pass


class CollaborativeArticleFeedGroup(UserFeedGroup):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="collab_article_groups",
        related_query_name="collab_article_groups",
    )


class CollabBasedRecommendedArticles(object):
    group = models.OneToOneField()
    feeds = models.ManyToManyField()

    class Meta:
        pass
