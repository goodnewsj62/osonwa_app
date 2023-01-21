from datetime import datetime, timezone as tz

from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from account.models import Notification, Profile, User, Interest
from utils.permissions import IsUserAccount, LockOut
from osonwa.helpers import get_auth_token
from account.helpers import (
    create_social_account,
    shorten_token,
    extract_data_from_token,
)
from osonwa.decorators import ensure_atomic
from utils.gen_helpers import generate_jwt_token
from account.oauth import TwitterHelper
from account.tasks import send_email
from account.serializers import (
    NotificationSerializer,
    ProfileSerializer,
    GoogleAuthSerializer,
    GoogleSignUpSerializer,
    CustomTokenObtainPairSerializer,
    TwitterAuthSerializer,
    TwitterSignupSerializer,
    FacebookSerializer,
    FacebookSignUpSerializer,
    ChangePasswordSerializer,
)

# Create your views here.


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


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


class FacebookLoginView(APIView):
    @method_decorator(ensure_atomic)
    def post(self, request, format=None):
        serializer = FacebookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_data = serializer.validated_data.get("token")
        social_id = user_data.get("id")
        user_ = User.objects.filter(email=user_data.get("email"))
        user = user_.first()
        if user_.filter(social_accounts__social_id=social_id).exists():
            # generate_token
            resp = get_auth_token(user)
            return Response(resp)

        elif user_.exists():
            create_social_account(user, social_id, "facebook")
            resp = get_auth_token(user)
            return Response(resp)

        return Response(
            {
                "message": {
                    "url": reverse("auth:fb_signup"),
                    "email": user_data.get("email"),
                }
            },
            status=status.HTTP_308_PERMANENT_REDIRECT,
        )


class FaceBookSignupView(APIView):
    def post(self, request, format=None):
        serializer = FacebookSignUpSerializer(data=request.data)
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

    @method_decorator(ensure_atomic)
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

        resp = {
            "url": reverse("auth:tw_signup"),
            "email": email,
            "social_id": social_id,
        }
        return Response({"message": resp}, status=status.HTTP_308_PERMANENT_REDIRECT)


class TwitterSignUpView(APIView):
    def post(self, request, format=None):
        serializer = TwitterSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        resp = get_auth_token(user)
        return Response(resp)


class PasswordChangeView(APIView):
    def get(self, request, format=None):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)

        payload = {"user_id": user.id, "email": user.email}
        token = generate_jwt_token(payload, exp=datetime.now(tz=tz.utc))
        key = shorten_token(token)
        send_email.delay(email, key)  # async function
        return Response({"message": "success"})

    def post(self, request, format=None):
        data = extract_data_from_token(request.data)
        if not data:
            message = {"error": ["token expired or defective"]}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        serializer = ChangePasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "success"})


class AccountProfileView(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related("user").prefetch_related(
        "user__interests"
    )
    permission_classes = [IsUserAccount]
    serializer_class = ProfileSerializer
    lookup_field = "username"

    def get_object(self):
        queryset = self.get_queryset()
        lookup = "user__" + self.lookup_field
        filter_ = {lookup: self.kwargs[self.lookup_field]}
        obj = get_object_or_404(queryset, **filter_)
        self.check_object_permissions(self.request, obj.user)
        return obj

    def get_permissions(self):
        perm_classes = self.permission_classes
        if self.action in ["list", "create"]:
            return [LockOut()]
        return [perm() for perm in perm_classes]


@api_view(["delete"])
def remove_interests(request, *args, **kwargs):
    interest = request.data.get("interest")
    if not interest:
        message = {"error": ["interest  field is required"]}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    interest = Interest.objects.filter(name=interest).first()

    if not interest:
        message = {"error": ["no such interest exists"]}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    interest.users.remove(request.user)
    return Response({"message": "success"})
