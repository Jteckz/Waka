from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.accounts.managers import UserManager
from common.constants import RoleChoices
from common.models import TimestampedMixin


class User(AbstractUser, TimestampedMixin):
    # Keep AbstractUser's auto-incrementing integer pk (BigAutoField via
    # DEFAULT_AUTO_FIELD). Django's auth infrastructure (sessions, relations,
    # admin) is tightly coupled to integer primary keys on the User model.
    # Switching to UUID would require extensive patching of contrib.auth
    # internals and provides no practical benefit for this project's scale.
    username = None
    phone = models.CharField(max_length=20, unique=True, db_index=True)

    role = models.CharField(max_length=20, choices=RoleChoices.choices)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["role"]

    objects = UserManager()

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.phone
