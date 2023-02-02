from rest_framework import serializers


from blog.models import Bundle, Post, Tags, PostImages
from account.serializers import UserSerializer


class BundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bundle
        fields = "__all__"
        extra_kwargs = {"created_by": {"required": False}}


class CustomTagSerializer(serializers.ModelSerializer):
    post = None

    class Meta:
        model = Tags
        fields = "__all__"
        extra_kwargs = {}


class PostSerializer(serializers.ModelSerializer):
    tags = CustomTagSerializer(many=True, required=False)
    author = UserSerializer(required=False)
    likes = serializers.SerializerMethodField("get_likes_count")
    bundle_name = serializers.StringRelatedField(source="bundle.topic")

    class Meta:
        model = Post
        fields = "__all__"
        extra_kwargs = {"author": {"required": False}}

    def validate(self, attrs):
        request = self.context.get("request")

        if request.method.lower() in ["put", "patch"]:
            self.validate_bundle_order()

        return super().validate(attrs)

    def get_likes_count(self, instance):
        return instance.likes.count()

    def to_representation(self, instance):
        resp = super().to_representation(instance)
        resp["content"] = instance.content.delta
        return resp

    def validate_bundle(self, value):
        if not value.created_by == self.context.get("request").user:
            raise serializers.ValidationError("can only add to a bundle you created")
        return value

    def validate_bundle_order(self):
        order = self.initial_data.get("order")
        bundle_id = self.initial_data.get("bundle")
        bundle = Bundle.objects.prefetch_related("posts").filter(id=bundle_id)
        post_id = self.context.get("post_id")

        if Post.objects.get(post_id=post_id).bundle == bundle.first():
            # case when user did not change the bundle
            return

        order_exists = bundle.filter(posts__order=order).exists()
        if order and order_exists:
            message = "An article with this order number exists. Please change the order and retry"
            raise serializers.ValidationError(message)


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImages
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    post = PostSerializer(many=True, required=False)

    class Meta:
        model = Tags
        fields = ["id","tag_name", "post"]
        extra_kwargs = {}
