from collections import OrderedDict

from rest_framework import serializers


class UserRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return super().to_representation(value)


class PostRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        response = OrderedDict()

        return super().to_representation(value)


class ContentTypeRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.model_class().__name__.lower()
