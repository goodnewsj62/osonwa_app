from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from account.models import Notification, Profile, SocialAccount, User
from account.oauth import GoogleHelper, FacebookHelper
from account.helpers import perform_user_creation


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        extra_kwargs = {}


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        extra_kwargs = {}


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
