from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

from common.constants import RoleChoices


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, password=None, role=None, **extra_fields):
        if not phone:
            raise ValueError(_("Phone number is required"))
        role = role or RoleChoices.MINOR_AGENT
        extra_fields.setdefault("is_active", True)
        user = self.model(phone=phone, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("role", RoleChoices.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(phone, password, **extra_fields)
