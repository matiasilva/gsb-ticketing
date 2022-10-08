from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models

from .enums import UserAuthType


class PaymentMethodManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class PaymentMethod(models.Model):
    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)


class User(AbstractUser):
    # see https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#fields
    # fields inherited: username, first name, last name, email, password,
    # groups, user_permissions, is_staff, is_active, is_superuser, last_login
    # date_joined

    kind = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, related_name='users'
    )

    auth_type = models.IntegerField(
        choices=UserAuthType.choices, default=UserAuthType.RAVEN
    )

    has_signed_up = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_first_own_ticket(self):
        return self.tickets.filter(is_own=False).count() == 0


class TicketKindManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class TicketKind(models.Model):

    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    requires_first = models.BooleanField(default=False)

    class Meta:
        db_table = 'ticketkinds'

    def __str__(self):
        return self.name


class UserKind(models.Model):
    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    # ideally make this many-to-many relation
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, related_name='users_kinds'
    )
    allowance = models.IntegerField()
    ticket_kinds = models.ManyToManyField(TicketKind, db_table="userkind_ticketkinds")

    objects = PaymentMethodManager()


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
    date_applied = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    # ticket type
    kind = models.ForeignKey(
        TicketKind, on_delete=models.CASCADE, related_name='tickets'
    )

    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, related_name='tickets'
    )
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
        constraints = [
            models.UniqueConstraint(
                fields=['purchaser'],
                condition=models.Q(is_own=True),
                name='unique_own_ticket_user',
            ),
            models.CheckConstraint(
                check=models.Q(dob__lte=date(2005, 3, 17)), name="minimum_age_check"
            ),
        ]

    def __str__(self):
        return f"{self.kind} {self.purchaser}"

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


class UserType(models.Model):
    class Meta:
        db_table = 'usertypes'

    pass
