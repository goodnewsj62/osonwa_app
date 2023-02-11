from rest_framework import serializers

from account.external_serializer import UserSerializer
from .models import Saved, Liked
from .drf_helpers import PostSerializer
from .relations import ContentTypeRelatedField


class SavedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    content_type = ContentTypeRelatedField(read_only=True)
    content_object = PostSerializer(required=False)

    class Meta:
        model = Saved
        fields = "__all__"


class LikedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    content_type = ContentTypeRelatedField(read_only=True)
    content_object = PostSerializer(required=False)

    class Meta:
        model = Liked
        fields = "__all__"
