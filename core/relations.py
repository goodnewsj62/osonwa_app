from rest_framework import serializers


class ContentTypeRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.model_class().__name__.lower()
