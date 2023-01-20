from rest_framework import serializers

from blog.models import Bundle, Post, Tags


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        extra_kwargs = {}


class BundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bundle
        fields = "__all__"
        extra_kwargs = {}


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"
        extra_kwargs = {}
