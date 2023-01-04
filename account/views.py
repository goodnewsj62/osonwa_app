from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, APIView

from account.models import Notification, Profile
from account.serializers import NotificationSerializer, ProfileSerializer

# Create your views here.


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
        # get my access token
        # validate my access token with is_valid
        # authenticate user and if such user exists
        # generate simple-jwt token
        pass


class GoogleSignup(APIView):
    def post(self, request, format=None):
        pass
