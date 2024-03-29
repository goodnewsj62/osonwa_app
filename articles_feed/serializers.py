from rest_framework import serializers

from articles_feed.models import ArticleFeed, ArticleReaction


class ArticleFeedSerializer(serializers.ModelField):
    class Meta:
        model = ArticleFeed
        fields = "__all__"
        extra_kwargs = {}
