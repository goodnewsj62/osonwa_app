from django.urls import reverse
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
    GoogleSignUpSerializer,
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


@api_view(["post"])
def verify_user_exists(request):
    email = request.data.get("email")
    user_id = request.data.get("user_id")

    user = User.objects.filter(email=email, social_accounts__social_id=user_id)
    if user.exists():
        return Response({"user_status": True})
    return Response({"user_status": False})


class GoogleLoginView(APIView):
    def post(self, request, format=None):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data.get("token")
        user = User.objects.filter(
            email=user_data.get("email"),
            social_accounts__social_id=user_data.get("sub"),
        )
        if user.exists():
            # generate_token
            resp = get_auth_token(user)
            return Response(resp)
        return Response(
            {"message": {"url": reverse("auth:g_signup")}},
            status=status.HTTP_308_PERMANENT_REDIRECT,
        )


class GoogleSignup(APIView):
    def post(self, request, format=None):
        serializer = GoogleSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response = get_auth_token(instance)
        return Response(response)
