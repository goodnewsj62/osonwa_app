from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from account.custom_manger import UserManager

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        _("email address"),
        max_length=300,
        unique=True,
    )
    first_name = models.CharField(
        _("first name"), max_length=300, null=False, blank=False
    )
    last_name = models.CharField(
        _("last name"), max_length=300, null=False, blank=False
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        pass

    def __repr__(self):
        return f"<{self.email}>"

    def __str__(self):
        return f"{self.email}"

    def get_full_name(self):
        return self.first_name + " " + self.last_name


class Profile(models.Model):
    user = models.OneToOneField(
        "account.User",
        null=True,
        on_delete=models.CASCADE,
        related_name="profile",
        related_query_name="profile",
    )
    image = models.ImageField(upload_to="images/profile/", default="images/default.jpg")
