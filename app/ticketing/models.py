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
    purchaser = models.ForeignKey(User, on_delete=models.CASCADE)

    # attendee details
    name = models.CharField(max_length='100')
    email = models.EmailField(blank=True)
    dob = models.DateField()

    # internal
    is_own = models.BooleanField()
    date_applied = models.DateField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    # ticket type
    class TicketType(models.IntegerChoices):
        STANDARD = 0, 'Standard'
        QUEUE_JUMP = 1, 'Queue Jump'

    kind = models.IntegerField(choices=TicketType.choices)

    # payment!
    class PaymentMethod(models.IntegerChoices):
        COLLEGE_BILL = 0, 'College Bill'
        BANK_TRANSFER = 1, 'Bank Transfer'
        CONCESSION = 2, 'Concession'

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
