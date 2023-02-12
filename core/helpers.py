from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status


from articles_feed.models import ArticleFeed
from news.models import NewsFeed
from blog.models import Post


def get_model_from_type(type_):
    strategies = {
        "post": Post,
        "article": ArticleFeed,
        "news": NewsFeed,
        "comment": None,
    }

    return strategies[type_]


def get_content_query(type_):
    if type_ == "article":
        post_type = ContentType.objects.get_for_model(Post)
        article_type = ContentType.objects.get_for_model(ArticleFeed)
        return Q(content_type__pk=article_type.pk) | Q(content_type__pk=post_type.pk)
    news_type = ContentType.objects.get_for_model(NewsFeed)
    return Q(content_type__pk=news_type.pk)


def get_resource_if_exists(type_, pk):
    model = get_model_from_type(type_)
    queryset = model.objects.filter(id=pk)
    if not queryset.exists():
        message = {"error": ["no such posts exists"]}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    return queryset.first()
