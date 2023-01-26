from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, APIView
from django.db.models import Prefetch

from blog.models import Post
from blog.serializers import PostSerializer

# Create your views here.


class PostViewSet(APIView):
    queryset = Post.objects.select_related("bundle", "author").prefetch_related(
        Prefetch("tags")
    )
    lookup_field = ["slug", "post_id"]
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    # implement patch, post and put


class PostBundleViewSet(viewsets.ModelViewSet):

    pass


class PostReaction(viewsets.ModelViewSet):
    pass


class TagViewSet(viewsets.ModelViewSet):
    pass
