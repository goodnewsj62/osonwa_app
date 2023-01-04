from rest_framework import serializers

from account.models import Notification, Profile, SocialAccount, User
from account.oauth import GoogleHelper
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


class GoogleSignInSerializer(GoogleAuthSerializer, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data: dict):
        data = validated_data.pop("token")

        user_id = data["sub"]
        provider = "google"

        user = perform_user_creation(provider, user_id, **validated_data)
        return user
