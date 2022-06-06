from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None, **others):
        if not email:
            raise ValueError("Users must have an email address")

        user_instance = self.model.create(email, first_name, last_name, **others)
        user_instance.set_password(password)
        user_instance.save()
        return user_instance

    def create_superuser(self, email, first_name, last_name, password=None, **others):
        others.setdefault("is_superuser", True)
        others.setdefault("is_staff", True)
        others.setdefault("is_active", True)
        return self.create_user(email, first_name, last_name, password, **others)
