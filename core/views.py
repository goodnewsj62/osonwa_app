from rest_framework.decorators import APIView, permission_classes, api_view
from rest_framework import status, permissions, pagination
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from .models import Liked, Saved
from .serializers import LikedSerializer, SavedSerializer
from .helpers import get_content_query, get_model_from_type, queryset_if_exists

# Create your views here.
class LikedView(APIView, pagination.PageNumberPagination):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None, *args, **kwargs):
        type_ = request.query_params.get("type", "article")
        user = get_user_model().objects.filter(pk=kwargs.get("pk")).first()
        if request.user != user:
            message = {"error": ["you cannot access another user resource"]}
            return Response(message, status=status.HTTP_403_FORBIDDEN)

        content_type_query = get_content_query(type_)
        queryset = user.liked.filter(content_type_query).all()

        page = self.paginate_queryset(queryset, request, self)
        serializer = LikedSerializer(instance=page, many=True)
        return self.get_paginated_response(serializer.data)

    def patch(self, request, format=None, *args, **kwargs):
        type_ = request.data.get("type", "article")

        returned_instance = queryset_if_exists(type_, kwargs.get("pk"))

        if isinstance(returned_instance, Response):
            return returned_instance

        queryset = returned_instance
        like = queryset.filter(likes__user__pk=request.user.pk)

        if like.exists():
            queryset.first().likes.remove(like)
            return Response({"message": "unliked"})

        Liked.objects.create(user=request.user, content_object=queryset.first())
        return Response({"message": "liked"})


class SavedView(APIView, pagination.PageNumberPagination):
    def get(self, request, format=None, *args, **kwargs):
        type_ = request.query_params.get("type", "article")
        user = get_user_model().objects.filter(pk=kwargs.get("pk")).first()
        if request.user != user:
            message = {"error": ["you cannot access another user resource"]}
            return Response(message, status=status.HTTP_403_FORBIDDEN)

        content_type_query = get_content_query(type_)
        queryset = user.saved.filter(content_type_query).all()
        page = self.paginate_queryset(queryset, request, self)
        serializer = SavedSerializer(instance=page, many=True)
        return self.get_paginated_response(serializer.data)

    def patch(self, request, format=None, *args, **kwargs):
        type_ = request.data.get("type", "article")

        returned_instance = queryset_if_exists(type_, kwargs.get("pk"))

        if isinstance(returned_instance, Response):
            return returned_instance

        queryset = returned_instance
        saved = queryset.filter(saved__user__pk=request.user.pk)

        if saved.exists():
            queryset.first().likes.remove(saved)
            return Response({"message": "saved"})

        Saved.objects.create(user=request.user, content_object=queryset.first())
        return Response({"message": "saved"})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def is_liked(self, request, *args, **kwargs):
    returned_instance = queryset_if_exists(kwargs.get("type"), kwargs.get("pk"))
    if isinstance(returned_instance, Response):
        return returned_instance

    instance = returned_instance.first()
    status = Liked.objects.filter(content_object=instance, user=request.user).exists()
    return Response({"message": status})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def is_saved(self, request, *args, **kwargs):
    returned_instance = queryset_if_exists(kwargs.get("type"), kwargs.get("pk"))
    if isinstance(returned_instance, Response):
        return returned_instance

    instance = returned_instance.first()
    status = Saved.objects.filter(content_object=instance, user=request.user).exists()
    return Response({"message": status})
