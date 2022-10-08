from django.db import models


class UserAuthType(models.TextChoices):
    RAVEN = 0, 'Raven'
    MANUAL = 1, 'Manual'
