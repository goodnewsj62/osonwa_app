from django.urls import reverse
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import Notification, Profile, User
from osonwa.helpers import get_auth_token
from account.helpers import create_social_account
from osonwa.decorators import ensure_atomic
from account.oauth import TwitterHelper
from account.serializers import (
    NotificationSerializer,
    ProfileSerializer,
    GoogleAuthSerializer,
    GoogleSignUpSerializer,
    CustomTokenObtainPairSerializer,
    TwitterAuthSerializer,
    TwitterSignupSerializer,
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
    @method_decorator(ensure_atomic)
    def post(self, request, format=None):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data.get("token")
        social_id = user_data.get("sub")
        user_ = User.objects.filter(email=user_data.get("email"))
        user = user_.first()
        if user_.filter(social_accounts__social_id=social_id).exists():
            # generate_token
            resp = get_auth_token(user)
            return Response(resp)
        elif user_.exists():
            create_social_account(user, social_id, "google")
            resp = get_auth_token(user)
            return Response(resp)

        return Response(
            {
                "message": {
                    "url": reverse("auth:g_signup"),
                    "email": user_data.get("email"),
                }
            },
            status=status.HTTP_308_PERMANENT_REDIRECT,
        )


class GoogleSignup(APIView):
    def post(self, request, format=None):
        serializer = GoogleSignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response = get_auth_token(instance)
        return Response(response)


class UserNameExistsCheck(APIView):
    def get(self, request, format=None):
        username = request.query_params.get("username")
        status = User.objects.filter(username=username).exists()
        return Response({"status": status})


class TwitterSignInView(APIView):
    api_helper = TwitterHelper()

    def get(self, request, format=None):
        redirect_url = self.api_helper.get_request_token()
        return Response({"url": redirect_url})

    def post(self, request, format=None):
        context = {"api_object": self.api_helper}
        serializer = TwitterAuthSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get("email_provided")
        social_id = serializer.validated_data.get("social_id")

        user_queryset = User.objects.filter(email=email)
        user = user_queryset.first()

        if user_queryset.filter(social_accounts__social_id=social_id).exists():
            return Response(get_auth_token(user))
        elif user_queryset.exists():
            create_social_account(user, social_id, "twitter")
            return Response(get_auth_token(user))

        resp = {"url": reverse("auth:tw_signup"), "email": email}
        return Response({"message": resp}, status=status.HTTP_308_PERMANENT_REDIRECT)


class TwitterSignUpView(APIView):
    api_helper = TwitterHelper()

    def post(self, request, format=None):
        context = {"api_object": self.api_helper}
        serializer = TwitterSignupSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        resp = get_auth_token(user)
        return Response(resp)
