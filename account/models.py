from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from account.custom_manger import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", max_length=300, unique=True)
    username = models.CharField(max_length=300, unique=True, blank=False, null=False)
    first_name = models.CharField("first name", max_length=300, null=False, blank=True)
    last_name = models.CharField("last name", max_length=300, null=False, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        pass

    def __repr__(self):
        return f"<{self.email}>"

    def __str__(self):
        return f"{self.email}"

    def get_full_name(self):
        return self.first_name + " " + self.last_name


class SocialAccount(models.Model):
    SOCIAL_CHOICES = [
        ("github", "github"),
        ("twitter", "twitter"),
        ("apple", "apple"),
        ("linkedin", "linkedin"),
        ("goolge", "google"),
    ]

    social_id = models.TextField()
    provider = models.CharField(
        max_length=20, choices=SOCIAL_CHOICES, blank=False, null=False
    )
    user = models.ForeignKey(
        "account.User",
        null=False,
        on_delete=models.CASCADE,
        related_name="social_accounts",
        related_query_name="social_accounts",
    )

    class Meta:
        verbose_name_plural = "social accounts"

    def __repr__(self):
        return f"<{self.user.email}>"

    def __str__(self):
        return f"{self.user.email}"


class Profile(models.Model):
    user = models.OneToOneField(
        "account.User",
        null=True,
        on_delete=models.CASCADE,
        related_name="profile",
        related_query_name="profile",
    )
    image = models.ImageField(upload_to="images/profile/", default="images/default.jpg")
    newsletter_notification = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "profile"

    def __repr__(self):
        return f"<{self.user.email}>"

    def __str__(self):
        return f"{self.user.email}"


class Notification(models.Model):
    ACTIONS = [("comment", "comment"), ("react", "react")]

    owner = models.ForeignKey(
        "account.User",
        null=False,
        on_delete=models.CASCADE,
        related_name="notifications",
        related_query_name="notifications",
    )

    action_by = models.ForeignKey("account.User", null=False, on_delete=models.CASCADE)
    action = models.CharField(max_length=80, choices=ACTIONS, blank=False, null=False)
    post_url = models.URLField()
    post_content = models.TextField(null=False, blank=False)
    is_read = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "notification"
        verbose_name_plural = "notifications"

    def __repr__(self):
        return f"<{self.owner.email}>"

    def __str__(self):
        return f"{self.owner.email}"
