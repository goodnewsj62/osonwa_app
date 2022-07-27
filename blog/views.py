from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, APIView

from blog.models import Post
from blog.serializers import PostSerializer

# Create your views here.


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()  # TODO: prefetch and the other needed
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


class PostBundleViewSet(viewsets.ModelViewSet):

    pass


class PostReaction(viewsets.ModelViewSet):
    pass


class TagViewSet(viewsets.ModelViewSet):
    pass
