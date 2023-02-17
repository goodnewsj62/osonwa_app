from rest_framework.decorators import APIView, permission_classes, api_view, action
from rest_framework import permissions, pagination
from rest_framework.response import Response
from django.db.models import Q

from .abs_view import BaseReactionView
from .models import Liked, Saved
from .serializers import LikedSerializer, SavedSerializer
from .helpers import get_content_query, get_resource_if_exists

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
        .filter(Q(article__title__iconatins=query) | Q(post__title__icontains=query))
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
        .filter(Q(article__title__iconatins=query) | Q(post__title__icontains=query))
        .all()
    )
    paginator = pagination.PageNumberPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = SavedSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)
