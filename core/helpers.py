from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status


from articles_feed.models import ArticleFeed, ArticleTag
from news.models import NewsFeed, NewsTag
from blog.models import Post, Tags
from osonwa.constants import article_fields, post_fields
from .drf_helpers import PostSerializer, TagPostSerializer
from .models import Comment


def get_model_from_type(type_):
    strategies = {
        "post": Post,
        "article": ArticleFeed,
        "news": NewsFeed,
        "comment": Comment,
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


def get_queryset_and_serializer(type_, tag_name):
    types = {"article": get_for_article, "news": get_for_news}
    return types[type_](tag_name)


def get_queryset(model, tag_name):
    return model.objects.filter(tag_name=tag_name).first().posts.all()


def get_for_article(tag_name):

    article_qs = get_queryset(ArticleTag, tag_name).values_list(
        **article_fields, named=True
    )
    post_qs = get_queryset(Tags, tag_name).values_list(**post_fields, named=True)
    return post_qs.union(article_qs).order_by("-date_published"), TagPostSerializer


def get_for_news(tag_name):
    return get_queryset(NewsTag, tag_name), PostSerializer


def get_content_type(self, type_):
    model = get_model_from_type(type_)
    return ContentType.objects.get_for_model(model)


def is_child_to_comment(comment):
    return isinstance(comment.content_object, Comment)


def set_mentions(mentions: list, instance):
    User = get_user_model()
    users = User.objects.filter(username__in=[mentions]).all()
    instance.mentions.set(list(users))
