from rest_framework import serializers

from account.models import User, Profile

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
