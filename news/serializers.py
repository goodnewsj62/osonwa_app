from rest_framework import serializers

from news.models import NewsFeed, NewsReaction


class NewsFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsFeed
        fields = "__all__"
        extra_kwargs = {}


class NewsReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsReaction
        fields = "__all__"
        extra_kwargs = {}
