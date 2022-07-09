from django.db import IntegrityError
import pytest

from news.models import (
    CollabBasedRecommendedNewsFeed,
    CollaborativeNewsFeedGroup,
    ContentBasedRecommendedNewsFeed,
    ContentNewsFeedGroups,
    NewsReaction,
)
from osonwa.assert_helpers import assert_true


def test_feed_gid_null_constraint(db, newsfeed_a):
    with pytest.raises(IntegrityError):
        newsfeed_a.gid = None
        newsfeed_a.save()


def test_feed_gid_unique_constraint(db, newsfeed_a, newsfeed):
    with pytest.raises(IntegrityError):
        newsfeed.gid = newsfeed_a.gid
        newsfeed.save()


def test_feed_empty_title(db, newsfeed_a):
    with pytest.raises(IntegrityError):
        newsfeed_a.title = None
        newsfeed_a.save()


def test_feed_with_empty_date(db, newsfeed_a):
    with pytest.raises(IntegrityError):
        newsfeed_a.date_published = None
        newsfeed_a.save()


def test_feed_reaction_model(db, newsreaction):
    assert_true(NewsReaction.objects.filter(pk=newsreaction.pk).exists())


def test_collab_group_creation(db, collabgroup_a, user_a):
    queryset = CollaborativeNewsFeedGroup.objects.filter(pk=collabgroup_a.pk)
    assert_true(queryset.exists())
    assert_true(queryset.first().users.filter(pk=user_a.pk).exists())


def test_collab_recommended(db, collab_recommeded):
    queryset = CollabBasedRecommendedNewsFeed.objects.filter(pk=collab_recommeded.pk)
    assert_true(queryset.exists())


def test_content_recommended(db, content_recommended_a, newsfeed_a):
    queryset = ContentBasedRecommendedNewsFeed.objects.filter(
        pk=content_recommended_a.pk
    )
    assert_true(queryset.exists())
    assert_true(queryset.first().feeds.filter(pk=newsfeed_a.pk).exists())


def test_content_group_creation(db, contentgroup_a, user):
    queryset = ContentNewsFeedGroups.objects.filter(pk=contentgroup_a.pk)
    assert_true(queryset.exists())
    assert_true(queryset.first().users.filter(pk=user.pk).exists())
