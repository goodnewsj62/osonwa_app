from collections import OrderedDict
from django.http import QueryDict
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.models import Notification, Profile, SocialAccount, User
from account.oauth import GoogleHelper, FacebookHelper
from account.helpers import perform_user_creation
from utils.gen_helpers import setattr_if_exists


class ProfileMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileMinSerializer(required=False)

    class Meta:
        model = User
        exclude = [
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
            "last_login",
        ]
        extra_kwargs = {"password": {"write_only": True, "required": False}}


class ProfileSerializer(serializers.ModelSerializer):
    interests = serializers.StringRelatedField(source="user.interests", many=True)
    user = UserSerializer(many=False, required=False)

    class Meta:
        model = Profile
        fields = "__all__"
        extra_kwargs = {}

    def validate(self, attrs):
        username = attrs.get("username")
        current_user = self.context.get("request").user
        user_exists = (
            User.objects.exclude(id=current_user.id).filter(username=username).exists()
        )
        if username and user_exists:
            raise serializers.ValidationError("username already exists")
        return super().validate(attrs)

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user = instance.user

        setattr_if_exists(user, user_data)
        user.save()

        setattr_if_exists(instance, validated_data)
        instance.save()

        return instance

    def to_internal_value(self, data):
        user_data = OrderedDict()
        for field, value in data.items():
            if field in ["username", "first_name", "last_name"]:
                user_data[field] = value
        data = data.copy() if isinstance(data, QueryDict) else data
        data["user"] = user_data
        return super().to_internal_value(data)

    def to_representation(self, instance):
        resp = super().to_representation(instance)
        user = resp.pop("user")
        response = OrderedDict(user)
        response.update(resp)
        return response


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        extra_kwargs = {}


class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = "__all__"
        extra_kwargs = {}


class GoogleAuthSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate_token(self, token):
        status, data = GoogleHelper.verify(token)
        if not status:
            raise serializers.ValidationError("Login unsuccessful")
        return data


class GoogleSignUpSerializer(GoogleAuthSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"required": False}}

    def create(self, validated_data: dict):
        data = validated_data.pop("token")

        user_id = data["sub"]
        provider = "google"

        user = perform_user_creation(provider, user_id, **validated_data)
        return user


class FacebookSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    user_id = serializers.CharField(required=True)

    def validate(self, data):
        token = data.get("token")
        user_id = data.get("user_id")
        status, user_info = FacebookHelper.verify(token, user_id)
        if not status:
            raise serializers.ValidationError("Login unsuccessful")

        data["token"] = user_info
        return data


class FacebookSignUpSerializer(FacebookSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"required": False}}

    def create(self, validated_data: dict):
        data = validated_data.pop("token")

        user_id = data["id"]
        provider = "facebook"

        user = perform_user_creation(provider, user_id, **validated_data)
        return user


class TwitterAuthSerializer(serializers.Serializer):
    oauth_token = serializers.CharField(
        required=True, allow_blank=False, allow_null=False
    )
    oauth_verifier = serializers.CharField(
        required=True, allow_blank=False, allow_null=False
    )
    social_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    email_provided = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )

    def validate(self, data):
        api_object = self.context.get("api_object")
        status, info = api_object.get_user_info(
            data["oauth_token"], data["oauth_verifier"]
        )
        if status:
            data["social_id"] = info.get("social_id")
            data["email_provided"] = info.get("email")
        else:
            raise serializers.ValidationError("could not fetch user information")
        return data


class TwitterSignupSerializer(serializers.ModelSerializer):
    social_id = serializers.CharField(
        required=True, allow_null=False, allow_blank=False
    )
    email = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {"password": {"required": False}}

    def create(self, validated_data: dict):
        user_id = validated_data.pop("social_id")

        user = perform_user_creation("twitter", user_id, **validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        tokens = super().get_token(user)
        # tokens["type"] = "login"

        return tokens


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    email = serializers.EmailField(required=True, allow_null=False, allow_blank=False)

    def validate_password(self, password):
        if len(password) < 8:
            raise serializers.ValidationError("must exceed 7 characters")
        return password

    def create(self, validated_data):
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return user


class InterestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
