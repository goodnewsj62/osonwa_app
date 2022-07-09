import factory

from factories import FeedFactory, FeedGroupFactory, ReactionFactory


class ArticleFeedFactory(FeedFactory):
    class Meta:
        model = "articles_feed.ArticleFeed"


class ArticleReactionFactory(ReactionFactory):
    class Meta:
        model = "articles_feed.ArticleReaction"

    post = factory.SubFactory(ArticleFeedFactory)


class ColabGroupFactory(FeedGroupFactory):
    class Meta:
        model = "articles_feed.CollaborativeArticleFeedGroup"


class CollabRecommendedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "articles_feed.CollabBasedRecommendedArticle"

    group = factory.SubFactory(ColabGroupFactory)


class ContentGroup(FeedGroupFactory):
    class Meta:
        model = "articles_feed.ContentArticleFeedGroup"


class ContentRecommendedFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "articles_feed.ContentBasedRecommendedArticle"

    group = factory.SubFactory(ContentGroup)
