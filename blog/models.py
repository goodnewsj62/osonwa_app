from uuid import uuid4

from django.db import models
from django.utils import timezone
from django_quill.fields import QuillField

from osonwa.resuable_models import UserReaction

# Create your models here.

# -tags
class Post(models.Model):
    ref = models.CharField(unique=True, max_length=20, blank=False, null=False)
    title = models.CharField("title", max_length=300, blank=False, null=False)
    cover_image = models.ImageField(
        upload_to="/images/cover_images", default="/images/blogdefault.jpg"
    )
    date_published = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(default=timezone.now)
    content = QuillField()
    author = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="posts",
    )

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        ordering = ["-date_updated"]

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f"<{self.title}>"


class PostImages(models.Model):
    reg = models.UUIDField(default=uuid4)
    post = models.ForeignKey(
        "blog.Post",
        null=True,
        on_delete=models.CASCADE,
        related_name="images",
        related_query_name="images",
    )

    image_url = models.ImageField(
        upload_to="images/blog_images/", null=False, blank=False
    )

    class Meta:
        verbose_name_plural = "posts images"

    def __str__(self) -> str:
        return self.reg

    def __repr__(self) -> str:
        return f"{str(self.reg)[:7]}"


class Tags(models.Model):
    tag_name = models.CharField("tags", max_length=300, unique=True, null=False)
    posts = models.ManyToManyField(
        "blog.Post", related_name="tags", related_query_name="tags"
    )

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self) -> str:
        return self.tag_name


class PostsUserReactions(UserReaction):
    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        related_name="reactions",
        related_query_name="reactions",
    )
