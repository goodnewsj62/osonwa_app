from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django_quill.fields import QuillField

# Create your models here.


class GenericRelationship(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True


class Saved(GenericRelationship):
    user = models.ForeignKey(
        "account.User",
        related_name="saved",
        related_query_name="saved",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-date_created"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.user.username


class Liked(GenericRelationship):

    user = models.ForeignKey(
        "account.User",
        related_name="liked",
        related_query_name="liked",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["-date_created"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.user.username


class Comment(GenericRelationship):
    created_by = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="comments",
        related_query_name="comment",
    )
    mentions = models.ManyToManyField(
        "account.User", related_name="mentions", related_query_name="mention"
    )
    content = QuillField()
    text_content = models.TextField()
    likes = GenericRelation(Liked, related_query_name="comment")
    comments = GenericRelation("self", related_query_name="comment")

    class Meta:
        ordering = ["-date_created"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return self.created_by.username


class SocialHandlesPosted(GenericRelationship):
    media_name = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)

    def get_model_type(self):
        return self.content_type.model_class().__name__.lower()

    def __str__(self) -> str:
        return f"{self.get_model_type()}: {self.object_id}"
