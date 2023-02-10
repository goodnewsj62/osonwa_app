from rest_framework import serializers

from account.models import User


class UserSerializer(serializers.ModelSerializer):
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
