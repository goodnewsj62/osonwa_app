from rest_framework.decorators import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from .serializers import LikedSerializer, SavedSerializer
from articles_feed.models import ArticleFeed
from news.models import NewsFeed
from blog.models import Post

# Create your views here.
class LikeArticlesView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        type_ = request.query_params().get("type", "articles")
        user = get_user_model().objects.filter(pk=kwargs.get("pk")).first()
        if request.user != user:
            message = {"error": ["you cannot access another user resource"]}
            return Response(message, status=status.HTTP_403_FORBIDDEN)

        content_type_query = self.get_content_query(type_)
        queryset = user.liked.filter(content_type_query).all()
        serializer = LikedSerializer(instance=queryset, many=True)
        return Response(serializer.data)

    def get_content_query(self, type_):
        if type_ == "article":
            article_type = ContentType.get_object_for_this_type(ArticleFeed)
            post_type = ContentType.get_object_for_this_type(Post)
            return Q(content_type__pk=article_type.pk) | Q(
                content_type__pk=post_type.pk
            )

        news_type = ContentType.get_object_for_this_type(NewsFeed)
        return Q(content_type__pk=news_type.pk)

    def patch(self, request, format=None, *args, **kwargs):
        pass


class SavedArticlesView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        pass

    def patch(self, request, format=None, *args, **kwargs):
        pass


def is_liked(self, request):
    pass


def is_saved(self, request):
    pass
