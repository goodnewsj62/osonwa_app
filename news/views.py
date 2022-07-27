from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, APIView
from news.models import NewsReaction

from news.serializers import NewsFeedSerializer, NewsReactionSerializer

# Create your views here.


class NewsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NewsFeedSerializer

    def get_queryset(self):
        return

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(method=["get"], detail=False, url_path="trending", url_name="trending")
    def trending(self, *args, **kwargs):
        return Response()

    @action(method=["get"], detail=False, url_path="fresh", url_name="fresh")
    def fresh(self, *args, **kwargs):
        return Response()

    @action(method=["get"], detail=False, url_name="search", url_path="search")
    def search(self, *args, **kwargs):
        return Response()


class NewsReactionViewSet(viewsets.ModelViewSet):
    queryset = NewsReaction.objects.all()
    serializer_class = NewsReactionSerializer
    permission_classes = [permissions.IsAuthenticated]
