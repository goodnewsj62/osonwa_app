from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import SimpleRouter


from .views import PostBundleViewSet, PostViewSet, TagViewSet

app_name = "blog"

router = SimpleRouter()
router.register("bundle", PostBundleViewSet, basename="bundle")
router.register("tag", PostBundleViewSet, basename="tag")

post_list = PostViewSet.as_view({"get": "list", "post": "create"})
post_detail = PostViewSet.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update"}
)

urlpatterns = [
    path("post/", post_list, name="post-list"),
    path("post/<str:slug_title>/<str:post_id>/", post_detail, name="post-detail"),
]

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
