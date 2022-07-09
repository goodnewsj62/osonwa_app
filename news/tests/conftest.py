import pytest
from pytest_factoryboy import LazyFixture, register

from news.factories import (
    NewsFeedFactory,
    NewsReactionFactory,
    CollabRecommendedFactory,
    ColabGroupFactory,
    ContentGroup,
    ContentRecommendedFactory,
)


factory_name_list = [
    (NewsFeedFactory, "newsfeed"),
    # more to be added
]


for factory_tuple in factory_name_list:
    register(factory_tuple[0], factory_tuple[1] + "_a")
    register(factory_tuple[0], factory_tuple[1])


@pytest.fixture
def newsreaction(db):
    return NewsReactionFactory.create()


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
def collab_recommeded(db, newsfeed):
    instance = CollabRecommendedFactory.create()
    instance.feeds.add(newsfeed)
    return instance


@pytest.fixture
def collab_recommended_a(db, newsfeed_a):
    instance = CollabRecommendedFactory.create()
    instance.feeds.add(newsfeed_a)
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
def content_recommeded(db, newsfeed):
    instance = ContentRecommendedFactory.create()
    instance.feeds.add(newsfeed)
    return instance


@pytest.fixture
def content_recommended_a(db, newsfeed_a):
    instance = ContentRecommendedFactory.create()
    instance.feeds.add(newsfeed_a)
    return instance
