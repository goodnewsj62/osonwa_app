from pickletools import pyset
import pytest
from pytest_factoryboy import register

from articles_feed.factories import (
    ArticleFeedFactory,
    ArticleReactionFactory,
    CollabRecommendedFactory,
    ColabGroupFactory,
    ContentGroup,
    ContentRecommendedFactory,
)


factory_name_list = [
    (ArticleFeedFactory, "articlefeed"),
    # more factories
]


for factory_tuple in factory_name_list:
    register(factory_tuple[0], factory_tuple[1] + "_a")
    register(factory_tuple[0], factory_tuple[1])


@pytest.fixture
def articlereaction(db):
    return ArticleReactionFactory.create()


@pytest.fixture
def collabgroup_a(db, user_a):
    instance = ColabGroupFactory.create()
    instance.users.add(user_a)
    return instance


@pytest.fixture
def collabgroup_b(db, user):
    instance = ColabGroupFactory.create()
    instance.users.add(user)
    return instance


@pytest.fixture
def collab_recommeded(db, articlefeed):
    instance = CollabRecommendedFactory.create()
    instance.feeds.add(articlefeed)
    return instance


@pytest.fixture
def collab_recommended_a(db, articlefeed_a):
    instance = CollabRecommendedFactory.create()
    instance.feeds.add(articlefeed_a)
    return instance


@pytest.fixture
def contentgroup_a(db, user):
    instance = ContentGroup.create()
    instance.users.add(user)
    return instance


@pytest.fixture
def contentgroup_b(db, user_a):
    instance = ContentGroup.create()
    instance.users.add(user_a)
    return instance


@pytest.fixture
def content_recommeded(db, articlefeed):
    instance = ContentRecommendedFactory.create()
    instance.feeds.add(articlefeed)
    return instance


@pytest.fixture
def content_recommended_a(db, articlefeed_a):
    instance = ContentRecommendedFactory.create()
    instance.feeds.add(articlefeed_a)
    return instance
