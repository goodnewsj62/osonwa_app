from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, APIView
from articles_feed.models import ArticleReaction


from articles_feed.serializers import ArticleFeedSerializer, ArticleReactionSerializer

# Create your views here.


class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ArticleFeedSerializer

    def get_queryset(self):
        return

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(method=["get"], detail=False, url_path="popular", url_name="popular")
    def popular(self, *args, **kwargs):
        return Response()

    @action(method=["get"], detail=False, url_path="fresh", url_name="fresh")
    def fresh(self, *args, **kwargs):
        return Response()

    @action(method=["get"], detail=False, url_name="search", url_path="search")
    def search(self, *args, **kwargs):
        return Response()


class ArticleReactionViewSet(viewsets.ModelViewSet):
    queryset = ArticleReaction.objects.all()
    serializer_class = ArticleReactionSerializer
    permission_classes = [permissions.IsAuthenticated]
