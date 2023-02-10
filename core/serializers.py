from rest_framework import serializers

from .models import Saved, Liked


class SavedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saved
        fields = ["user", "content_type", "content_object", "content_id"]


class LikedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Liked
        fields = ["user", "content_type", "content_object", "content_id"]
