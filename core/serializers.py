from rest_framework import serializers

from account.external_serializer import UserSerializer
from .models import Saved, Liked
from .drf_helpers import PostSerializer
from .relations import ContentTypeRelatedField


class SavedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    content_type = ContentTypeRelatedField()
    content_object = PostSerializer(required=False)

    class Meta:
        model = Saved
        fields = ["user", "content_type", "content_object", "content_id"]


class LikedSerializer(serializers.ModelSerializer):
    content_type = ContentTypeRelatedField()
    content_object = PostSerializer(required=False)

    class Meta:
        model = Liked
        fields = ["user", "content_type", "content_object", "content_id"]
