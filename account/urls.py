from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import verify_user_exists, GoogleLoginView, GoogleSignup

app_name = "auth"

urlpatterns = [
    path("google/", GoogleLoginView.as_view(), name="g_login"),
    path("g_signup/", GoogleSignup.as_view(), name="g_signup"),
    path("verify/", verify_user_exists, name="verify"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
