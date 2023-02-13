from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import SimpleRouter


from .views import PostBundleViewSet, PostViewSet, TagViewSet, user_post

app_name = "blog"

router = SimpleRouter()
router.register("bundle", PostBundleViewSet, basename="bundle")
router.register("tag", TagViewSet, basename="tag")

post_list = PostViewSet.as_view({"get": "list", "post": "create"})
post_detail = PostViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update"}
)
set_tags = PostViewSet.as_view({"patch": "add_tag"})

urlpatterns = [
    path("post/", post_list, name="post-list"),
    path("post/<str:slug_title>/<str:post_id>/", post_detail, name="post-detail"),
    path("post/add-tag/<str:slug_title>/<str:post_id>/", set_tags, name="add_tag"),
    path("user-post/<str:username>/", user_post, name="user_post"),
]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
