from datetime import timedelta

from django.shortcuts import get_object_or_404
from rest_framework.decorators import APIView, permission_classes, api_view, action
from rest_framework import permissions, pagination, viewsets, status
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone

from utils.permissions import IsOwner, LockOut
from news.models import NewsFeed
from blog.models import Post
from articles_feed.models import ArticleFeed
from osonwa.constants import post_fields, article_fields
from .abs_view import BaseReactionView, BaseAggApiView
from .models import Liked, Saved, Comment
from .drf_helpers import PostSerializer, ArticleUnionSerializer
from .serializers import LikedSerializer, SavedSerializer, CommentSerializer
from .recommended import get_recommended_news_feed, get_recommended_article_feed
from .helpers import (
    get_content_query,
    get_resource_if_exists,
    get_queryset_and_serializer,
    get_content_type,
    get_articles_qs,
    create_comment_notification,
    order_by_interactions,
)

# Create your views here.


class LikedView(BaseReactionView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, model_type="like", *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, model_type="like", *args, **kwargs)


class SavedView(BaseReactionView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, model_type="save", *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, model_type="save", *args, **kwargs)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def is_liked(request, *args, **kwargs):
    type_ = kwargs.get("type")
    returned_instance = get_resource_if_exists(type_, kwargs.get("pk"))
    if isinstance(returned_instance, Response):
        return returned_instance

    instance = returned_instance
    filter_ = {type_: instance}
    status = Liked.objects.filter(user=request.user, **filter_).exists()
    return Response({"message": status})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def is_saved(request, *args, **kwargs):
    type_ = kwargs.get("type")
    returned_instance = get_resource_if_exists(type_, kwargs.get("pk"))
    if isinstance(returned_instance, Response):
        return returned_instance

    instance = returned_instance
    filter_ = {type_: instance}
    status = Saved.objects.filter(user=request.user, **filter_).exists()
    return Response({"message": status})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def search_like(request, *args, **kwargs):
    type_ = request.query_params.get("type", "article")
    query = request.query_params.get("q", "")
    content_type_query = get_content_query(type_)
    queryset = (
        request.user.liked.filter(content_type_query)
        .filter(
            Q(article__title__icontains=query)
            | Q(post__title__icontains=query)
            | Q(news__title__icontains=query)
        )
        .all()
    )
    paginator = pagination.PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = LikedSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def search_saved(request, *args, **kwargs):
    type_ = request.query_params.get("type", "article")
    query = request.query_params.get("q", "")
    content_type_query = get_content_query(type_)
    queryset = (
        request.user.saved.filter(content_type_query)
        .filter(
            Q(article__title__icontains=query)
            | Q(post__title__icontains=query)
            | Q(news__title__icontains=query)
        )
        .all()
    )
    paginator = pagination.PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = SavedSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


class TagsView(APIView, pagination.PageNumberPagination):
    def get(self, request, *args, **kwargs):
        tag_name = request.query_params.get("name", "")
        type_ = request.query_params.get("type", "article")
        queryset, serializer = get_queryset_and_serializer(type_, tag_name)
        page = self.paginate_queryset(queryset, request, self)
        serializer = serializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)


class CommentView(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        elif self.action == "create":
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsOwner()]

    def get_serializer(self, *args, **kwargs):
        serializer = CommentSerializer(
            *args, **kwargs, context={"request": self.request}
        )
        return serializer

    def get_queryset(self, *args, **kwargs):
        queryset = Comment.objects.select_related("created_by").prefetch_related(
            "mentions"
        )
        if self.action == "list":
            return queryset.filter(**kwargs).all()
        return queryset

    def list(self, request, *args, **kwargs):
        type_ = request.query_params.get("type", "article")
        id_ = request.query_params.get("id")
        content_type = get_content_type(type_)
        queryset = self.get_queryset(content_type__pk=content_type.id, object_id=id_)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=["get"], detail=False, url_name="ucomments", url_path="ucomments")
    def usercomments(self, request, *args, **kwargs):
        username = request.query_params.get("username")
        if not username:
            message = "please include userame in url query param"
            return Response({"error": message}, status=status.HTTP)
        queryset = (
            self.get_queryset()
            .filter(created_by__username=username)
            .order_by("-date_created")
            .all()
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        create_comment_notification(creator=self.request.user, comment=instance)
        return instance


class NewsView(viewsets.ModelViewSet):
    lookup_field = ["slug_title", "pk"]

    def get_object(self):
        query_set = self.get_queryset()
        filters = {}
        for field in self.lookup_field:
            filters[field] = self.kwargs[field]

        obj = get_object_or_404(query_set, **filters)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        if not self.request.method in permissions.SAFE_METHODS:
            return [LockOut()]
        return [permissions.AllowAny()]

    def get_serializer(self, *args, **kwargs):
        ctx = {"request": self.request}
        return PostSerializer(*args, **kwargs, context=ctx)

    def get_queryset(self):
        queryset = NewsFeed.objects.prefetch_related(
            "tags", "comments", "likes"
        ).order_by("-date_published")
        is_authenticated = self.request.user.is_authenticated
        if self.action == "list" and is_authenticated:
            recommended = get_recommended_news_feed(self.request.user)
            queryset = queryset.filter(id__in=recommended) if recommended else queryset
            return queryset
        return queryset


class TrendingView(BaseAggApiView):
    def get_queryset(self, type_):
        """
        order queryset by date_published and interactions rate(comments and likes)...
        if user is authenticated recommended post are retrieved for the user
        """
        if type_ == "article":
            queryset = ArticleFeed.objects
            if self.request.user.is_authenticated:
                recommended = get_recommended_article_feed(self.request.user)
                queryset = (
                    queryset.filter(id__in=recommended) if recommended else queryset
                )

            article_qs = self.order_by_interactions(queryset)
            post_qs = self.order_by_interactions(Post.objects)
            return (
                post_qs.values_list(*post_fields, named=True)
                .union(article_qs.values_list(*article_fields, named=True))
                .order_by("-date_published")
            )
        else:
            queryset = NewsFeed.objects
            if self.request.user.is_authenticated:
                recommended = get_recommended_news_feed(self.request.user)
                queryset = (
                    queryset.filter(id__in=recommended) if recommended else queryset
                )

            return self.order_by_interactions(queryset)

    def order_by_interactions(self, qs):
        return order_by_interactions(qs)


class FreshView(BaseAggApiView):
    def get_queryset(self, type_):
        if type_ == "article":
            queryset = ArticleFeed.objects.filter(date_published__gt=self.yesterday)
            post_qs = Post.objects.filter(date_published__gt=self.yesterday)
            if self.request.user.is_authenticated:
                recommended = get_recommended_article_feed(self.request.user)
                queryset = (
                    queryset.filter(id__in=recommended) if recommended else queryset
                )

            article_qs = queryset.order_by("-date_published")
            post_qs = post_qs.order_by("-date_published")
            return (
                post_qs.values_list(*post_fields, named=True)
                .union(article_qs.values_list(*article_fields, named=True))
                .order_by("-date_published")
            )
        else:
            queryset = NewsFeed.objects.filter(date_published__gt=self.yesterday)
            if self.request.user.is_authenticated:
                recommended = get_recommended_news_feed(self.request.user)
                queryset = (
                    queryset.filter(id__in=recommended) if recommended else queryset
                )

            return queryset.order_by("-date_published")

    @property
    def yesterday(self):
        return timezone.now() - timedelta(days=2)


@api_view(["get"])
def banner_news(request, *args, **kwargs):
    queryset = (
        NewsFeed.objects.exclude(image_url=None)
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
        .order_by("-date_published", "-likes_count", "-comments_count")[:7]
    )

    serializer = PostSerializer(queryset, many=True, context={"request": request})
    return Response(serializer.data)


class ArticleView(viewsets.ModelViewSet):
    lookup_field = ["slug_title", "pk"]

    def get_object(self):
        query_set = self.get_queryset()
        filters = {}
        for field in self.lookup_field:
            filters[field] = self.kwargs[field]

        obj = get_object_or_404(query_set, **filters)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_permissions(self):
        if not self.request.method in permissions.SAFE_METHODS:
            return [LockOut()]
        return [permissions.AllowAny()]

    def get_serializer(self, *args, **kwargs):
        ctx = {"request": self.request}
        return PostSerializer(*args, **kwargs, context=ctx)

    def get_queryset(self):
        queryset = ArticleFeed.objects.prefetch_related(
            "tags", "comments", "likes"
        ).order_by("-date_published")
        is_authenticated = self.request.user.is_authenticated
        if self.action == "list" and is_authenticated:
            recommended = get_recommended_news_feed(self.request.user)
            queryset = queryset.filter(id__in=recommended) if recommended else queryset
            return queryset
        return queryset

    def list(self, request, *args, **kwargs):
        filter_params = request.query_params.get("filter", "[]")

        type_ = request.query_params.get("type", "internal")
        qs = get_articles_qs(filter_params, type_, request)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=["get"], detail=False, url_name="search", url_path="search")
    def search(self, request, *args, **kwargs):
        search_kw = request.query_params.get("q")
        type_ = request.query_params.get("type")
        if type_ == "internal":
            qs = Post.objects.filter(title__icontains=search_kw).order_by(
                "-date_published"
            )
        else:
            qs = (
                self.get_queryset()
                .filter(title__icontains=search_kw)
                .order_by("-date_published")
            )

        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class SearchView(APIView, pagination.PageNumberPagination):
    def get(self, request, *args, **kwargs):
        search = request.query_params.get("q")
        article_qs = ArticleFeed.objects.filter(title__icontains=search).values_list(
            *article_fields, named=True
        )
        news_qs = NewsFeed.objects.filter(title__icontains=search).values_list(
            *article_fields, named=True
        )
        post_qs = Post.objects.filter(title__icontains=search).values_list(
            *post_fields, named=True
        )

        queryset = post_qs.union(article_qs, news_qs).order_by("-date_published")
        page = self.paginate_queryset(queryset, request, self)
        serializer = ArticleUnionSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class WebsiteView(APIView, pagination.PageNumberPagination):
    def get(self, request, *args, **kwargs):
        type_ = request.query_params.get("type")
        website = request.query_params.get("name")
        qs = (
            ArticleFeed.objects.filter(website=website)
            if type_ == "article"
            else NewsFeed.objects.filter(website=website)
        )
        page = self.paginate_queryset(qs.order_by("-date_published"), request, self)
        ctx = {"request": request}
        serializer = PostSerializer(page, many=True, context=ctx)
        return self.get_paginated_response(serializer.data)
