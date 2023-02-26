import re
from rest_framework import serializers

from account.models import User
from account.external_serializer import UserSerializer


class ContentTypeRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.model_class().__name__.lower()


class MentionsRelated(serializers.RelatedField):
    def get_queryset(self):
        return User.objects.all()

    def to_representation(self, value):
        return UserSerializer(value.all(), many=True).data

    def to_internal_value(self, mentions):
        data = []
        if not isinstance(mentions, list):
            raise serializers.ValidationError("an array or list of username expected")

        for mention in mentions:
            if not isinstance(mention, str):
                raise serializers.ValidationError(
                    "each value in mentions must be of type string"
                )
            
            if self.is_corrupted(mention): continue
            data.append(mention.replace(r"@", ""))
        return data
    
    def is_corrupted(self,mention):
        return re.search(r"^@(http|https|ftp|ftps|wss|ws)",mention)
