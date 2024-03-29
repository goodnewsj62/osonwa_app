from django.contrib.auth import get_user_model
from rest_framework import status, pagination
from rest_framework.decorators import APIView
from rest_framework.response import Response

from .helpers import get_content_query, get_resource_if_exists, create_like_notification
from .models import Liked, Saved
from .serializers import LikedSerializer, SavedSerializer
from .drf_helpers import PostSerializer, ArticleUnionSerializer


class BaseReactionView(APIView, pagination.PageNumberPagination):
    def get(self, request, *args, **kwargs):
        type_ = request.query_params.get("type", "article")
        user = get_user_model().objects.filter(pk=kwargs.get("pk")).first()
        if request.user != user:
            message = {"error": ["you cannot access another user resource"]}
            return Response(message, status=status.HTTP_403_FORBIDDEN)

        queryset = self.get_queryset(user, type_, **kwargs)

        page = self.paginate_queryset(queryset, request, self)
        ctx = {"request": request}
        serializer = self.get_serializer(
            kwargs.get("model_type"),
            instance=page,
            many=True,
            context=ctx,
        )
        return self.get_paginated_response(serializer.data)

    def patch(self, request, *args, **kwargs):
        type_ = request.data.get("type", "article")

        returned_instance = get_resource_if_exists(type_, kwargs.get("pk"))

        if isinstance(returned_instance, Response):
            return returned_instance

        model_type = kwargs.get("model_type")
        model = self.get_model(model_type)

        post = returned_instance
        queryset_obj = model.objects.filter(user__pk=request.user.pk, **{type_: post})

        if queryset_obj.exists():
            self.remove_queryset_obj(model_type, post, queryset_obj.first())
            return Response(self.get_response("remove", model_type))

        model.objects.create(user=request.user, content_object=post)
        if model_type == "like":
            create_like_notification(creator=request.user, post=post)
        return Response(self.get_response("create", model_type))

    def remove_queryset_obj(self, model_type, post, obj):
        if model_type == "like":
            return post.likes.remove(obj)
        elif model_type == "save":
            return post.saved.remove(obj)

    def get_model(self, model_type):
        return {"like": Liked, "save": Saved}[model_type]

    def get_response(self, action, model_type):
        response = {
            "like_remove": "unliked",
            "like_create": "liked",
            "save_remove": "unsaved",
            "save_create": "saved",
        }

        key = f"{model_type}_{action}"
        return {"message": response[key]}

    def get_queryset(self, user, type_, **kwargs):
        content_type_query = get_content_query(type_)
        operations = {
            "like": user.liked.filter(content_type_query).all(),
            "save": user.saved.filter(content_type_query).all(),
        }
        return operations[kwargs.get("model_type")]

    def get_serializer(self, typeof_serializer, *args, **kwargs):
        serializers = {"like": LikedSerializer, "save": SavedSerializer}
        return serializers[typeof_serializer](*args, **kwargs)


class BaseAggApiView(APIView, pagination.PageNumberPagination):
    def get(self, request, *args, **kwargs):
        type_ = request.query_params.get("type", "article")
        queryset = self.get_queryset(type_)
        page = self.paginate_queryset(queryset, request, self)
        serializer_class = self.get_serializer_class(type_)
        serializer = serializer_class(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    def get_serializer_class(self, type_):
        return ArticleUnionSerializer if type_ == "article" else PostSerializer

    def get_queryset(self, type_):
        raise NotImplementedError("overide get_queryset")
