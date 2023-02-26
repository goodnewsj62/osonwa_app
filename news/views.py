from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import APIView
from news.models import NewsTag

from news.serializers import NewsTagSerializer

# Create your views here.


class NewsTagListView(APIView):
    def get(self, request, *args, **kwargs):
        qs = NewsTag.objects.all()
        serializer = NewsTagSerializer(qs, many=True)
        return Response(serializer.data)
