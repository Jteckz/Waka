from django.db import models

from common.models import BaseModel


class NetworkTypeChoices(models.TextChoices):
    TELECOM = "TELECOM", "Telecom"
    BANK = "BANK", "Bank"


class Network(BaseModel):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    logo = models.URLField(max_length=500, blank=True, default="")
    network_type = models.CharField(max_length=20, choices=NetworkTypeChoices.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
