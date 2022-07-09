import factory

from factories import FeedFactory, FeedGroupFactory, ReactionFactory


class NewsFeedFactory(FeedFactory):
    class Meta:
        model = "news.NewsFeed"


class NewsReactionFactory(ReactionFactory):
    class Meta:
        model = "news.NewsReaction"

    post = factory.SubFactory("news.factories.NewsFeedFactory")


class ColabGroupFactory(FeedGroupFactory):
    class Meta:
        model = "news.CollaborativeNewsFeedGroup"


class CollabRecommendedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "news.CollabBasedRecommendedNewsFeed"

    group = factory.SubFactory(ColabGroupFactory)


class ContentGroup(FeedGroupFactory):
    class Meta:
        model = "news.ContentNewsFeedGroups"


class ContentRecommendedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "news.ContentBasedRecommendedNewsFeed"

    group = factory.SubFactory(ContentGroup)
