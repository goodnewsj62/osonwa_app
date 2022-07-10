from django.db import IntegrityError
import pytest

from articles_feed.models import (
    CollabBasedRecommendedArticle,
    CollaborativeArticleFeedGroup,
    ContentBasedRecommendedArticle,
    ContentArticleFeedGroup,
    ArticleReaction,
)
from osonwa.assert_helpers import assert_true


def test_articlefeed_gid_null_constraint(db, articlefeed_a):
    with pytest.raises(IntegrityError):
        articlefeed_a.gid = None
        articlefeed_a.save()


def test_articlefeed_gid_unique_constraint(db, articlefeed_a, articlefeed):
    with pytest.raises(IntegrityError):
        articlefeed.gid = articlefeed_a.gid
        articlefeed.save()


def test_articlefeed_empty_title(db, articlefeed_a):
    with pytest.raises(IntegrityError):
        articlefeed_a.title = None
        articlefeed_a.save()


def test_articlefeed_with_empty_date(db, articlefeed_a):
    with pytest.raises(IntegrityError):
        articlefeed_a.date_published = None
        articlefeed_a.save()


def test_articlefeed_reaction_model(db, articlereaction):
    assert_true(ArticleReaction.objects.filter(pk=articlereaction.pk).exists())


def test_collab_group_creation(db, collabgroup_a, user_a):
    queryset = CollaborativeArticleFeedGroup.objects.filter(pk=collabgroup_a.pk)
    assert_true(queryset.exists())
    assert_true(queryset.first().users.filter(pk=user_a.pk).exists())


def test_collab_recommended(db, collab_recommeded):
    queryset = CollabBasedRecommendedArticle.objects.filter(pk=collab_recommeded.pk)
    assert_true(queryset.exists())


def test_content_recommended(db, content_recommended_a, articlefeed_a):
    queryset = ContentBasedRecommendedArticle.objects.filter(
        pk=content_recommended_a.pk
    )
    assert_true(queryset.exists())
    assert_true(queryset.first().feeds.filter(pk=articlefeed_a.pk).exists())


def test_content_group_creation(db, contentgroup_a, user):
    queryset = ContentArticleFeedGroup.objects.filter(pk=contentgroup_a.pk)
    assert_true(queryset.exists())
    assert_true(queryset.first().users.filter(pk=user.pk).exists())
