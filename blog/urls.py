from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import SimpleRouter


from .views import PostBundleViewSet, PostViewSet, TagViewSet

app_name = "blog"

router = SimpleRouter()
router.register("post", PostViewSet, basename="post")
router.register("bundle", PostBundleViewSet, basename="bundle")
router.register("tag", PostBundleViewSet, basename="tag")

urlpatterns = []

urlpatterns += router.urls
urlpatterns = format_suffix_patterns(urlpatterns)
