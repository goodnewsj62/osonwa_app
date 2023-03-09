import json
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status


from articles_feed.models import ArticleFeed, ArticleTag
from news.models import NewsFeed, NewsTag
from blog.models import Post
from account.models import Notification
from osonwa.constants import article_fields, post_fields
from .drf_helpers import PostSerializer, ArticleUnionSerializer
from .models import Comment
from .recommended import get_recommended_article_feed


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
    return model.objects.filter(tag__tag_name=tag_name).all()


def get_for_article(tag_name):

    article_qs = get_queryset(ArticleFeed, tag_name).values_list(
        *article_fields, named=True
    )
    post_qs = get_queryset(Post, tag_name).values_list(*post_fields, named=True)
    return post_qs.union(article_qs).order_by("-date_published"), ArticleUnionSerializer


def get_for_news(tag_name):
    return get_queryset(NewsFeed, tag_name), PostSerializer


def get_content_type(type_):
    model = get_model_from_type(type_)
    return ContentType.objects.get_for_model(model)


def is_child_to_comment(comment):
    return isinstance(comment.content_object, Comment)


def set_mentions(mentions: list, instance):
    User = get_user_model()
    users = User.objects.filter(username__in=mentions).all()
    instance.mentions.set(list(users))


def get_articles_qs(params: str, type_: str, request):
    key_list = json.loads(params)
    fil = {
        "for you": for_you_qs(type_, request),
        "recent": recent_qs(type_),
        "popular": popular_qs(type_),
    }

    qs = Post.objects if type_ == "internal" else ArticleFeed.objects

    for key in key_list:
        qs = fil[key](qs)

    qs = qs.order_by("-date_published")
    return qs


def for_you_qs(type_, request):
    def _fyp(qs):
        if type_ == "aggregate" and request.user.is_authenticated:
            recommended = get_recommended_article_feed(request.user)
            return qs.filter(id__in=recommended) if recommended else qs
        return qs

    return _fyp


def recent_qs(type_):
    def _recent(qs):
        two_days_back = timezone.now() - timedelta(days=2)
        return qs.filter(date_published__gt=two_days_back)

    return _recent


def popular_qs(type_):
    def popular(qs):
        return qs.annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        ).order_by("-date_published", "-likes_count", "-comments_count")

    return popular


def create_comment_notification(creator, comment):
    content_type = comment.content_type
    if content_type.model_class().__name__.lower() == "comment":
        params = {
            "action_by": creator,
            "action": "mention",
            "content_object": comment.content_object,
        }
        if creator.id != comment.content_object.created_by.id:
            # no need for notification when i comment on my comment
            params = {**params, "action": "comment"}
            Notification.objects.create(
                **params, owner=comment.content_object.created_by
            )

        for user in comment.mentions.all():
            Notification.objects.create(**params, owner=user)

    elif content_type.model_class().__name__.lower() == "post":
        Notification.objects.create(
            action_by=creator,
            action="comment",
            content_object=comment.content_object,
            owner=comment.content_object.author,
        )


def create_like_notification(creator, post):
    if isinstance(post, Post):
        Notification.objects.create(
            action_by=creator,
            action="react",
            content_object=post,
            owner=post.author,
        )
    elif isinstance(post, Comment):
        Notification.objects.create(
            action_by=creator,
            action="react",
            content_object=post,
            owner=post.created_by,
        )
