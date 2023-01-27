from rest_framework import serializers


from blog.models import Bundle, Post, Tags, PostImages
from account.serializers import UserSerializer


class BundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bundle
        fields = "__all__"
        extra_kwargs = {}


class CustomTagSerializer(serializers.ModelSerializer):
    posts = None

    class Meta:
        model = Tags
        fields = "__all__"
        extra_kwargs = {}


class PostSerializer(serializers.ModelSerializer):
    tags = CustomTagSerializer(many=True, required=False)
    author = UserSerializer(required=False)
    likes = serializers.SerializerMethodField("get_likes_count")
    bundle_name = serializers.StringRelatedField(source="bundle.topic")

    class Meta:
        model = Post
        fields = "__all__"
        extra_kwargs = {"author": {"required": False}}

    def validate(self, attrs):
        order = attrs.get("order")
        bun_id = attrs.get("bundle")
        post_with_order = Bundle.objects.filter(id=bun_id, posts__order=order).exists()
        if order and post_with_order:
            raise serializers.ValidationError(
                "There is a post having this order number"
            )
        return super().validate(attrs)

    def get_likes_count(self, instance):
        return instance.likes.count()


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True)

    class Meta:
        model = Tags
        fields = "__all__"
        extra_kwargs = {}
