from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import Notification, Profile, User
from osonwa.helpers import get_auth_token
from account.serializers import (
    NotificationSerializer,
    ProfileSerializer,
    GoogleAuthSerializer,
    CustomTokenObtainPairSerializer,
)

# Create your views here.


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class SignupViewSet(viewsets.ViewSet):
    def create(self, *args, **kwargs):
        pass


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return


class BookmarkedViewSet(viewsets.ModelViewSet):
    pass


class GoogleLoginView(APIView):
    def post(self, request, format=None):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = User.objects.filter(
            email=validated_data.get("email"),
            social_accounts__social_id=validated_data.get("sub"),
        )
        if user.exists():
            # generate_token
            resp = get_auth_token(user)
            return Response(resp)
        return Response(
            {"message": "user does not exists"}, status=status.HTTP_404_NOT_FOUND
        )

    # @action(methods=["post"], detail=False, url_path="/verify")
    # def verify_details()


class GoogleSignup(APIView):
    def post(self, request, format=None):
        pass
