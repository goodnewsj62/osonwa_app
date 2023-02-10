from rest_framework import serializers


class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.SerializerMethodField()
    publisher = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    pub_image = serializers.SerializerMethodField()
    date_published = serializers.DateTimeField()
    tags = serializers.StringRelatedField(source="tags.tag_name", many=True)
    likes = serializers.SerializerMethodField()
    is_post = serializers.SerializerMethodField("is_post_check")
    # comments = serializers.SerializerMethodField()

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
        return self.get_attr_if_exists(instance, ["author", "website"], "publisher")

    def get_image(self, instance):
        if hasattr(instance, "cover_image"):
            return instance.cover_image.url
        return instance.image_url

    def get_pub_image(self, instance):
        if hasattr(instance, "logo_url"):
            return instance.logo_url
        return instance.author.profile.image.url

    def get_likes(self, instance):
        return instance.likes.count()

    # def get_comments(self, instance):
    #     return instance.comments.count()

    def is_post_check(self, instance):
        return not hasattr("gid", instance)
