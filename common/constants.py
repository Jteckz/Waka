from django.db import models


class RoleChoices(models.TextChoices):
    MASTER_AGENT = "MASTER_AGENT", "Master Agent"
    MINOR_AGENT = "MINOR_AGENT", "Minor Agent"
    ADMIN = "ADMIN", "Admin"


class RequestStatusChoices(models.TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    COMPLETED = "COMPLETED", "Completed"
