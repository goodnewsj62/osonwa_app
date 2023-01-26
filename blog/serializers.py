from rest_framework import serializers


from blog.models import Bundle, Post, Tags, PostImages
from account.serializers import UserSerializer


class BundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bundle
        fields = "__all__"
        extra_kwargs = {}


class TagSerializer(serializers.ModelSerializer):
    posts = None

    class Meta:
        model = Tags
        fields = "__all__"
        extra_kwargs = {}


class PostSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = UserSerializer(required=False)
    bundle_name = serializers.StringRelatedField(source="bundle.topic")

    class Meta:
        model = Post
        fields = "__all__"
        extra_kwargs = {"author": {"required": False}}

    def validate(self, attrs):
        order = attrs.get("order")
        post_with_order = Bundle.objects.filter(posts__order=order).exists()
        if order and post_with_order:
            raise serializers.ValidationError(
                "There is a post having this order number"
            )
        return super().validate(attrs)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = "__all__"
