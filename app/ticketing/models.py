from datetime import date

from django.db import models


class User(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField()
    name = models.CharField(max_length=100)

    class UserStatus(models.TextChoices):
        GIRTON_UGRAD = 0, 'Girton Undergraduate'
        GIRTON_PGRAD = 1, 'Girton Postgraduate'
        GIRTON_STAFF = 2, 'Girton Staff'
        GIRTON_ALUM = 3, 'Girton Alumnus/a'
        # UCAM_UGRAD, UCAM_PGRAD, EXTERNAL

    status = models.IntegerField(choices=UserStatus.choices)

    class UserAuthType(models.TextChoices):
        RAVEN = 0, 'Raven'
        MANUAL = 1, 'Manual'

    auth_type = models.IntegerField(
        choices=UserAuthType.choices, default=UserAuthType.RAVEN
    )

    is_authenticated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name


class Ticket(models.Model):
    class Meta:
        db_table = 'tickets'

    pass
