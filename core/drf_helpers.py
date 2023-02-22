from collections import OrderedDict

from rest_framework import serializers
from account.external_serializer import UserSerializer

from osonwa.constants import post_fields
from news.models import NewsFeed
from blog.models import Post
from account.external_serializer import UserSerializer
from articles_feed.models import ArticleFeed
from .models import Comment


class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    post_id = serializers.SerializerMethodField()
    title = serializers.CharField()
    slug_title = serializers.CharField()
    content = serializers.SerializerMethodField()
    publisher = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    pub_image = serializers.SerializerMethodField()
    date_published = serializers.DateTimeField()
    tags = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_post = serializers.SerializerMethodField("is_post_check")
    comments = serializers.SerializerMethodField()

    def get_attr_if_exists(self, instance, attrs, default_attr=""):
        for attr in attrs:
            if hasattr(instance, attr):
                return getattr(instance, attr)
        return getattr(instance, default_attr if default_attr else attrs[0])

    def get_content(self, instance):
        return self.get_attr_if_exists(
            instance, ["description", "text_content"], "content"
        )

    def get_publisher(self, instance):
        value = self.get_attr_if_exists(instance, ["author", "website"], "publisher")
        if isinstance(value, (str, int)):
            return value
        return UserSerializer(value).data

    def get_image(self, instance):
        if hasattr(instance, "cover_image"):
            return instance.cover_image.url if instance.cover_image else None
        return instance.image_url

    def get_pub_image(self, instance):
        if hasattr(instance, "logo_url"):
            return instance.logo_url
        return instance.author.profile.image.url

    def get_likes(self, instance):
        return instance.likes.count()

    def get_comments(self, instance):
        return instance.comments.count()

    def get_tags(self, instance):
        if hasattr(instance, "tags"):
            return list(instance.tags.values())
        return []

    def get_is_liked(self, instance):
        request = self.context.get("request")
        if request and request.user.pk:
            return instance.likes.filter(user__pk=request.user.pk).exists()
        return False

    def get_is_saved(self, instance):
        request = self.context.get("request")
        if request and request.user.pk:
            return instance.saved.filter(user__pk=request.user.pk).exists()
        return False

    def get_post_id(self, instance):
        return self.get_attr_if_exists(instance, ["post_id", "gid"])

    def is_post_check(self, instance):
        return not hasattr(instance, "gid")


class ArticleUnionSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        resp = OrderedDict()
        model = {"post": Post, "article": ArticleFeed}[instance.m_name]
        m_instance = model.objects.get(id=instance.id)

        for field in post_fields:
            resp[field] = getattr(instance, field, None)

        if instance.m_name != "article":
            resp["publisher"] = UserSerializer(m_instance.author).data
        else:
            resp["publisher"] = resp.pop("author__username", "")

        resp["pub_image"] = resp.pop("author__profile__image", "")
        resp["content"] = resp.pop("text_content")
        resp["image"] = resp.pop("cover_image")
        resp["tags"] = (
            list(m_instance.tags.values()) if hasattr(instance, "tags") else []
        )
        resp["likes"] = m_instance.likes.count()
        resp["is_liked"] = self.get_is_liked(m_instance)
        resp["is_saved"] = self.get_is_saved(m_instance)
        resp["is_post"] = m_instance.m_name == "post"
        resp["comments"] = m_instance.comments.count()

        return resp

    def get_is_liked(self, instance):
        request = self.context.get("request")
        if request and request.user.pk:
            return instance.likes.filter(user__pk=request.user.pk).exists()
        return False

    def get_is_saved(self, instance):
        request = self.context.get("request")
        if request and request.user.pk:
            return instance.saved.filter(user__pk=request.user.pk).exists()
        return False


class CommentSerializerExt(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

    def to_representation(self, instance):
        resp = super().to_representation(instance)
        resp["content"] = instance.content.delta
        resp["html"] = instance.content.html
        resp["mentions"] = UserSerializer(instance.mentions.all(), many=True).data
        return resp


class CommentSerializerMixin:
    def get_content_object(self, instance):
        instance_possibilites = [
            (NewsFeed, PostSerializer),
            (ArticleFeed, PostSerializer),
            (Comment, CommentSerializerExt),
        ]
        for model, serializers in instance_possibilites:
            if isinstance(instance.content_object, model):
                return serializers(instance.content_object).data
        return {}

    def get_post_info(self, instance):
        """there are only two level nesting"""
        if isinstance(instance.content_object, Comment):
            return PostSerializer(instance.content_object.content_object).data
        return PostSerializer(instance.content_object).data

    def get_likes_count(self, instance):
        return instance.likes.count()

    def get_comments_count(self, instance):
        return instance.comments.count()
