from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.


class GenericRelationship(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        abstract = True


class Saved(GenericRelationship):
    user = models.ForeignKey(
        "account.User", related_name="saved", related_query_name="saved"
    )

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.user.username


class Liked(GenericRelationship):

    user = models.ForeignKey(
        "account.User", related_name="liked", related_query_name="liked"
    )

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.user.username


# class Comments(GenericRelationship):
# user = models.ForeignKey(
#     "account.User", related_name="liked", related_query_name="liked"
# )

# class Meta:
#     indexes = [
#         models.Index(fields=["content_type", "object_id"]),
#     ]

# def __str__(self):
#     return self.user.username
