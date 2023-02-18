from django.urls import path
from rest_framework.routers import format_suffix_patterns

from .views import LikedView, SavedView, is_liked, is_saved, search_saved, search_like

app_name = "core"

urlpatterns = [
    path("liked/<int:pk>/", LikedView.as_view(), name="liked"),
    path("saved/<int:pk>/", SavedView.as_view(), name="saved"),
    path("is-liked/<str:type>/<int:pk>/", is_liked, name="is_liked"),
    path("is-saved/<str:type>/<int:pk>/", is_saved, name="is_saved"),
    path("search/saved/", search_saved, name="search_saved"),
    path("search/like/", search_like, name="search_liked"),
]
