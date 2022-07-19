from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self, email, username, first_name, last_name, password=None, **others
    ):

        if not email:
            raise ValueError("Users must have an email address")

        user_instance = self.model.objects.create(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **others
        )
        user_instance.set_password(password)
        user_instance.save()
        return user_instance

    def create_superuser(
        self, email, username, first_name, last_name, password=None, **others
    ):

        others = {"is_superuser": True, "is_staff": True, "is_active": True, **others}

        return self.create_user(
            email, username, first_name, last_name, password, **others
        )
