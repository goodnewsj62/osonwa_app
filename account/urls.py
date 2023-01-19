from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    verify_user_exists,
    GoogleLoginView,
    GoogleSignup,
    UserNameExistsCheck,
    TwitterSignInView,
    TwitterSignUpView,
    FacebookLoginView,
    FaceBookSignupView,
)

app_name = "auth"

urlpatterns = [
    path("google/", GoogleLoginView.as_view(), name="g_login"),
    path("g_signup/", GoogleSignup.as_view(), name="g_signup"),
    path("facebook/", FacebookLoginView.as_view(), name="facebook"),
    path("fb_signup/", FaceBookSignupView.as_view(), name="fb_signup"),
    path("twitter/", TwitterSignInView.as_view(), name="twitter"),
    path("tw_signup/", TwitterSignUpView.as_view(), name="tw_signup"),
    path("verify/user/", verify_user_exists, name="verify"),
    path("verify/username/", UserNameExistsCheck.as_view(), name="valid_username"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
