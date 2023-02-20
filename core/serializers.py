from rest_framework import serializers

from account.external_serializer import UserSerializer
from .models import Saved, Liked
from .drf_helpers import PostSerializer
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
