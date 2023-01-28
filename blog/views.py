from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.db.models import Prefetch

from utils.permissions import LockOut, IsOwner
from .models import Post, Bundle, Tags, PostImages
from .serializers import PostSerializer, BundleSerializer, TagSerializer

# Create your views here.


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("bundle", "author").prefetch_related(
        Prefetch("tags"), Prefetch("likes")
    )
    lookup_field = ["slug_title", "post_id"]
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_permissions(self):
        permissions_classes = self.permission_classes
        if self.action == "list":
            return [LockOut()]
        return [perm() for perm in permissions_classes]

    def get_object(self):
        query_set = self.get_queryset()
        filters = {}
        for field in self.lookup_field:
            filters[field] = self.kwargs[field]
        obj = get_object_or_404(query_set, **filters)
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.data)
        return Response(serializer.data)


class PostBundleViewSet(viewsets.ModelViewSet):
    serializer_class = BundleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_permissions(self):
        permissions_classes = self.permission_classes
        if self.action == "list":
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


class PostReaction(viewsets.ModelViewSet):
    pass


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.prefetch_related("posts")
    serializer_class = TagSerializer

    def get_permissions(self):
        if self.action in ["patial_update", "update"]:
            return [LockOut()]
        elif self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
