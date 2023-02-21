from rest_framework.decorators import APIView, permission_classes, api_view, action
from rest_framework import permissions, pagination, viewsets
from rest_framework.response import Response
from django.db.models import Q

from utils.permissions import IsOwner, LockOut
from news.models import NewsFeed
from articles_feed.models import ArticleFeed
from .abs_view import BaseReactionView
from .models import Liked, Saved, Comment
from .drf_helpers import PostSerializer
from .serializers import LikedSerializer, SavedSerializer, CommentSerializer
from .recommended import get_recommended_news_feed
from .helpers import (
    get_content_query,
    get_resource_if_exists,
    get_queryset_and_serializer,
    get_content_type,
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
        .filter(Q(article__title__icontains=query) | Q(post__title__icontains=query))
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
        .filter(Q(article__title__icontains=query) | Q(post__title__icontains=query))
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
        serializer = serializer(page)
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

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)


class NewsView(viewsets.ModelViewSet):
    serializer_class = PostSerializer

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

    def get_permissions(self):
        if not self.request.method in permissions.SAFE_METHODS:
            return [LockOut()]
        return [permissions.AllowAny()]
