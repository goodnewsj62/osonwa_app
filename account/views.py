from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, APIView

from account.models import Notification, Profile
from account.serializers import NotificationSerializer, ProfileSerializer

# Create your views here.


class SignupViewSet(viewsets.ViewSet):
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
