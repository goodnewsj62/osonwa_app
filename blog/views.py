from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action, api_view
from django.db.models import Prefetch

from utils.permissions import LockOut, IsOwner
from .models import Post, Bundle, Tags, PostImages
from .serializers import PostSerializer, BundleSerializer, TagSerializer

# Create your views here.


class PostViewSet(viewsets.ModelViewSet):
    lookup_field = ["slug_title", "post_id"]
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_permissions(self):
        permissions_classes = self.permission_classes
        if self.action == "list":
            return [permissions.IsAuthenticated()]
        elif self.action == "retrieve":
            return [permissions.AllowAny()]
        return [perm() for perm in permissions_classes]

    def get_queryset(self):
        queryset = Post.objects.select_related("bundle", "author").prefetch_related(
            Prefetch("tags"), Prefetch("likes")
        )

        if self.action == "list":
            queryset = queryset.filter(author=self.request.user)
        return queryset

    def get_serializer(self, *args, **kwargs):
        ctx = {"post_id": self.kwargs.get("post_id"), "request": self.request}
        return PostSerializer(*args, **kwargs, context=ctx)

    def get_object(self):
        query_set = self.get_queryset()
        filters = {}
        for field in self.lookup_field:
            filters[field] = self.kwargs[field]
        obj = get_object_or_404(query_set, **filters)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["patch"], detail=True, url_name="add_tag", url_path="add-tag")
    def add_tag(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            tags = request.data.get("tags")
            tags = [tag["id"] for tag in tags]
            instance.tags.set(tags)
            return Response({"message": "success"})
        except AttributeError:
            message = ["invalid format"]
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def user_post(request, *args, **kwargs):
    paginator = PageNumberPagination()
    paginator.page_size = 50
    username = kwargs.get("username", "")
    queryset = (
        Post.objects.select_related("bundle", "author")
        .prefetch_related(Prefetch("tags"), Prefetch("likes"))
        .filter(author__username=username)
    )
    page = paginator.paginate_queryset(queryset, request)
    serializer = PostSerializer(page, many=True, context={"request": request})
    return paginator.get_paginated_response(serializer.data)


class PostBundleViewSet(viewsets.ModelViewSet):
    serializer_class = BundleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_permissions(self):
        permissions_classes = self.permission_classes
        if self.action in ["list", "create"]:
            return [permissions.AllowAny()]
        return [perm() for perm in permissions_classes]

    def get_queryset(self):
        query_set = Bundle.objects.select_related("created_by")
        if self.action in ["list"]:
            return query_set
        return query_set.filter(created_by=self.request.user)

    @action(detail=False, url_name="my_bundles", url_path="my-bundles")
    def my_bundles(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(detail=False, url_name="search", url_path="search")
    def bundle_search(self, request, *args, **kwargs):
        topic = request.query_params.get("topic")
        instance = self.get_queryset().filter(topic__icontains=topic)
        serializer = self.get_serializer(instance=instance, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        return self.perform_create(serializer)


class PostReaction(viewsets.ModelViewSet):
    pass


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.prefetch_related("posts")
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action in ["partial_update", "update"]:
            return [LockOut()]
        elif self.action in ["list", "retrieve", "search"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    @action(methods=["get"], detail=False, url_name="search", url_path="search")
    def search(self, request, *args, **kwargs):
        keyword = request.query_params.get("keyword", "")
        queryset = self.get_queryset().filter(tag_name__icontains=keyword).all()[:15]
        serializer = self.get_serializer(instance=queryset, many=True)
        return Response(serializer.data)
