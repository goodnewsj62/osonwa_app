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
    PasswordChangeView,
    AccountProfileView,
    InterestsView,
    InterestsDetailView,
    NotificationView,
)

app_name = "auth"

profile = AccountProfileView.as_view({"get": "list"})
profile_view = AccountProfileView.as_view(
    {"get": "retrieve", "put": "update", "patch": "partial_update"}
)

urlpatterns = [
    path("google/", GoogleLoginView.as_view(), name="g_login"),
    path("g_signup/", GoogleSignup.as_view(), name="g_signup"),
    path("facebook/", FacebookLoginView.as_view(), name="facebook"),
    path("fb_signup/", FaceBookSignupView.as_view(), name="fb_signup"),
    path("twitter/", TwitterSignInView.as_view(), name="twitter"),
    path("tw_signup/", TwitterSignUpView.as_view(), name="tw_signup"),
    path("verify/user/", verify_user_exists, name="verify"),
    path("verify/username/", UserNameExistsCheck.as_view(), name="valid_username"),
    path("change-password/", PasswordChangeView.as_view(), name="password_change"),
    path("interests/", InterestsView.as_view(), name="interests"),
    path("interests/<str:username>/", InterestsDetailView.as_view(), name="d_interest"),
    path("profile/", profile, name="auth_user_profile"),
    path("profile/<str:username>/", profile_view, name="profile"),
    path("notification/", NotificationView.as_view(), name="notification"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
