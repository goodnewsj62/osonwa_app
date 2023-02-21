from rest_framework import serializers

from account.external_serializer import UserSerializer
from utils.gen_helpers import setattr_if_exists
from .models import Saved, Liked, Comment
from .helpers import is_child_to_comment, get_model_from_type, set_mentions
from .drf_helpers import PostSerializer, CommentSerializerMixin
from .relations import ContentTypeRelatedField


class SavedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    content_type = ContentTypeRelatedField(read_only=True)
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Saved
        fields = "__all__"

    def get_content_object(self, instance):
        ctx = self.context
        return PostSerializer(instance=instance.content_object, context=ctx).data


class LikedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    content_type = ContentTypeRelatedField(read_only=True)
    content_object = serializers.SerializerMethodField()

    class Meta:
        model = Liked
        fields = "__all__"

    def get_content_object(self, instance):
        ctx = self.context
        return PostSerializer(instance=instance.content_object, context=ctx).data


class TagSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tag_name = serializers.CharField()
    posts = PostSerializer(many=True, read_only=True)


class CommentSerializer(serializers.ModelSerializer, CommentSerializerMixin):
    created_by = UserSerializer(required=False)
    content_type = ContentTypeRelatedField(read_only=True)
    content_object = serializers.SerializerMethodField()
    post_info = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField("get_likes_count")
    comments = serializers.SerializerMethodField("get_comments_count")

    class Meta:
        model = Comment
        fields = "__all__"

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method.lower() != "post":
            return attrs

        if "post_id" not in attrs:
            raise serializers.ValidationError("post_id field is required")
        if "type" not in attrs:
            raise serializers.ValidationError("type field is required")

        model = get_model_from_type(attrs["type"])
        entity = model.objects.filter(id=attrs["post_id"])
        if not entity.exists():
            raise serializers.ValidationError("no entity exists with such post_id")

        if attrs["type"].startswith("comment"):
            comment = entity.first()
            message = "only two level nesting is allowed: cannot be a child of comment that is a child of comment"
            raise serializers.ValidationError(message) if is_child_to_comment(
                comment
            ) else None

        self.context = {**self.context, "content_object": entity.first()}

        return super().validate(attrs)

    def to_representation(self, instance):
        resp = super().to_representation(instance)
        resp["content"] = instance.content.delta
        resp["html"] = instance.content.html
        resp["mentions"] = UserSerializer(instance.mentions.all(), many=True).data
        return resp

    def create(self, validated_data):
        content_object = self.context.get("content_object")
        mentions = validated_data.pop("mentions", [])
        instance = Comment.objects.create(
            content_object=content_object, **validated_data
        )
        set_mentions(mentions, instance)
        return instance

    def update(self, instance, validated_data):
        validated_data.pop("created_by", "")
        mentions = validated_data.pop("mentions", [])
        mentions = set(
            [*instance.mentions.values_list("username", flat=True), *mentions]
        )
        set_mentions(list(mentions), instance)
        setattr_if_exists(instance, validated_data)
        instance.save()
        return instance
