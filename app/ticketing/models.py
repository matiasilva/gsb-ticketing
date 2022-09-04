from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # see https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#fields
    # fields inherited: username, first name, last name, email, password,
    # groups, user_permissions, is_staff, is_active, is_superuser, last_login
    # date_joined

    class UserStatus(models.IntegerChoices):
        GIRTON_UGRAD = 0, 'Girton Undergraduate'
        GIRTON_PGRAD = 1, 'Girton Postgraduate'
        GIRTON_STAFF = 2, 'Girton Staff'
        GIRTON_ALUM = 3, 'Girton Alumnus/a'
        UCAM_OTHER = 4, 'Cambridge University Member'
        # UCAM_UGRAD, UCAM_PGRAD, EXTERNAL

    status = models.IntegerField(
        choices=UserStatus.choices, default=UserStatus.UCAM_OTHER
    )

    class UserAuthType(models.TextChoices):
        RAVEN = 0, 'Raven'
        MANUAL = 1, 'Manual'

    auth_type = models.IntegerField(
        choices=UserAuthType.choices, default=UserAuthType.RAVEN
    )

    has_signed_up = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username


class Ticket(models.Model):
    class Meta:
        db_table = 'tickets'

    pass
