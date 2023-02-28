from django.urls import path
from rest_framework.routers import format_suffix_patterns, SimpleRouter

from .views import (
    LikedView,
    SavedView,
    CommentView,
    NewsView,
    TagsView,
    TrendingView,
    FreshView,
    ArticleView,
    SearchView,
    banner_news,
    is_liked,
    is_saved,
    search_saved,
    search_like,
)

app_name = "core"

router = SimpleRouter()
router.register("comment", CommentView, "comment")

news_list = NewsView.as_view({"get": "list"})
news_detail = NewsView.as_view({"get": "retrieve"})

article_detail = ArticleView.as_view({"get": "retrieve"})
article_list = ArticleView.as_view({"get": "list"})
article_search = ArticleView.as_view({"get": "search"})

urlpatterns = [
    path("liked/<int:pk>/", LikedView.as_view(), name="liked"),
    path("saved/<int:pk>/", SavedView.as_view(), name="saved"),
    path("is-liked/<str:type>/<int:pk>/", is_liked, name="is_liked"),
    path("is-saved/<str:type>/<int:pk>/", is_saved, name="is_saved"),
    path("search/saved/", search_saved, name="search_saved"),
    path("search/like/", search_like, name="search_liked"),
    path("news/", news_list, name="news"),
    path("news/<str:slug_title>/<int:pk>/", news_detail, name="news_detail"),
    path("article/<str:slug_title>/<int:pk>/", article_detail, name="article"),
    path("articles/", article_list, name="article_list"),
    path("article/search/", article_search, name="article_search"),
    path("trending/", TrendingView.as_view(), name="trending"),
    path("fresh/", FreshView.as_view(), name="fresh"),
    path("tags/", TagsView.as_view(), name="tags"),
    path("top-news/", banner_news, name="banner"),
    path("search/", SearchView.as_view(), name="search"),
]

urlpatterns += router.urls


urlpatterns = format_suffix_patterns(urlpatterns)
