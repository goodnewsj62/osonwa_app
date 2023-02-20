from uuid import uuid4

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django_quill.fields import QuillField
from django.template.defaultfilters import slugify
from django.core.validators import FileExtensionValidator
from django.contrib.contenttypes.fields import GenericRelation
from core.models import Liked, Saved


from osonwa.helpers import generate_b64_uuid_string, inmemory_wrapper
from osonwa.general_models import UserReaction, Tag

# Create your models here.


class Bundle(models.Model):
    topic = models.CharField(max_length=80, null=False, blank=False)
    poster = models.ImageField(
        upload_to="images/cover_images/",
        validators=[FileExtensionValidator(allowed_extensions=["jpeg", "jpg", "webp"])],
        null=True,
    )
    created_by = models.ForeignKey(
        "account.User",
        related_name="bundles",
        related_query_name="bundle",
        on_delete=models.CASCADE,
    )


# -tags
class Post(models.Model):
    post_id = models.CharField(unique=True, max_length=20, blank=True, null=True)
    title = models.CharField("title", max_length=300, blank=False, null=False)
    slug_title = models.SlugField(null=True, blank=True)
    cover_image = models.ImageField(
        upload_to="images/cover_images/",
        validators=[FileExtensionValidator(allowed_extensions=["jpeg", "jpg", "webp"])],
        null=True,
    )
    date_published = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(default=timezone.now)
    content = QuillField()
    text_content = models.TextField()
    author = models.ForeignKey(
        "account.User",
        null=False,
        on_delete=models.CASCADE,
        related_name="posts",
        related_query_name="posts",
    )
    bundle = models.ForeignKey(
        "blog.Bundle",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
        related_query_name="posts",
    )

    order = models.IntegerField(null=True)  # for bundle
    approved = models.BooleanField(default=True)
    likes = GenericRelation(Liked, related_query_name="post")
    saved = GenericRelation(Saved, related_query_name="post")

    class Meta:
        verbose_name = "post"
        verbose_name_plural = "posts"
        ordering = ["-date_updated"]

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f"<{self.title}>"

    def save(self, *args, **kwargs) -> None:
        self.post_id = self.create_post_id(self.post_id)
        self.slug_title = slugify(self.title)
        self.cover_image = inmemory_wrapper(
            self.cover_image, "/images/blogdefault.jpg", 1000
        )

        return super().save(*args, **kwargs)

    def create_post_id(self, post_id):
        if not post_id:
            return generate_b64_uuid_string()[:7]
        return post_id

    def get_absolute_ur(self):
        return reverse(
            "blog:post-detail",
            kwargs={"post_id": self.post_id, "slug_title": self.slug_title},
        )


class PostImages(models.Model):
    reg = models.UUIDField(default=uuid4)
    post = models.ForeignKey(
        "blog.Post",
        null=True,
        on_delete=models.CASCADE,
        related_name="images",
        related_query_name="images",
    )

    image = models.ImageField(upload_to="images/blog_images/", null=False, blank=False)

    class Meta:
        verbose_name_plural = "posts images"

    def __str__(self) -> str:
        return self.reg

    def __repr__(self) -> str:
        return f"{str(self.reg)[:7]}"

    def save(self, *args, **kwargs) -> None:
        self.image = inmemory_wrapper(self.image, "", 1000)
        return super().save(*args, **kwargs)


class Tags(Tag):
    posts = models.ManyToManyField(
        "blog.Post", related_name="tags", related_query_name="tags"
    )

    class Meta:
        verbose_name = "tag"
        verbose_name_plural = "tags"


class PostUserReactions(UserReaction):
    post = models.ForeignKey(
        "blog.Post",
        on_delete=models.CASCADE,
        related_name="reactions",
        related_query_name="reactions",
    )
