from django.urls import path
from .views import NewsTagListView

app_name = "news"
urlpatterns = [
    path("tags/", NewsTagListView.as_view(), name="tags"),
]
