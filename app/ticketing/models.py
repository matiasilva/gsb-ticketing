from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models

from .enums import (
    PAYMENT_METHOD_MAP,
    USER_TICKET_ALLOWANCE,
    PaymentMethod,
    TicketType,
    UserAuthType,
    UserStatus,
)


class User(AbstractUser):
    # see https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#fields
    # fields inherited: username, first name, last name, email, password,
    # groups, user_permissions, is_staff, is_active, is_superuser, last_login
    # date_joined

    status = models.IntegerField(
        choices=UserStatus.choices, default=UserStatus.UCAM_OTHER
    )

    auth_type = models.IntegerField(
        choices=UserAuthType.choices, default=UserAuthType.RAVEN
    )

    has_signed_up = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    def get_ticket_allowance(self):
        return USER_TICKET_ALLOWANCE[self.status]

    def get_payment_method(self):
        return PAYMENT_METHOD_MAP[self.status].label

    def is_first_ticket(self):
        return self.tickets.count() == 0

    def get_available_ticket_kinds(self):
        # account for ticket kind limits
        return TicketType.choices


class TicketKind(models.Model):

    name = models.CharField(max_length=100)
    price = models.IntegerField()

    class Meta:
        db_table = 'ticketkind'

    def __str__(self):
        return self.name


class Ticket(models.Model):
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tickets'
    )

    # attendee details
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    dob = models.DateField()

    # internal
    is_own = models.BooleanField()
    date_applied = models.DateField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    # ticket type
    kind = models.ForeignKey(
        TicketKind, on_delete=models.CASCADE, related_name='tickets'
    )

    payment_method = models.IntegerField(choices=PaymentMethod.choices)
    has_paid = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True)

    # TODO answers to questions
    # crsid, then use lookup to extract the below
    # affiliation: 31 colleges, none
    # degree level: ugrad, pgrad, alum, none
    # affiliation -> none implies external (non ucam)
    # degree level -> none but some affiliation implies staff

    # dietary requirements
    # drink preferences

    class Meta:
        db_table = 'tickets'

    def __str__(self):
        return f"{self.type} {self.purchaser}"

    def get_name(self):
        if self.is_own:
            return f"{self.purchaser.first_name} {self.purchaser.last_name}"
        else:
            return self.name

    def get_email(self):
        if self.is_own:
            return self.purchaser.email
        else:
            return self.email
