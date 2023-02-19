import random
from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class PaymentMethod(models.Model):
    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        managed = False


class TicketKind(models.Model):

    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    requires_first = models.BooleanField(default=False)

    class Meta:
        db_table = 'ticketkinds'
        managed = False

    def __str__(self):
        return f"{self.enum}"

    def is_available(self):
        return self.allocation.is_available()


class UserKind(models.Model):
    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    ticket_kinds = models.ManyToManyField(TicketKind, db_table="userkind_ticketkinds")

    def __str__(self):
        return self.name

    class Meta:
        managed = False


class User(models.Model):
    # strip down the AbstractBaseUser to its essentials

    username = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()

    # hard-coded..yikes!
    kind = models.ForeignKey(
        UserKind, on_delete=models.CASCADE, related_name='users', default=5
    )

    # optional fields
    matriculation_date = models.DateField(null=True)
    pname = models.CharField(max_length=100)
    psurname = models.CharField(max_length=100)

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = 'users'
        managed = False


class Ticket(models.Model):
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tickets'
    )

    # attendee details
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    # internal
    is_own = models.BooleanField()
    uuid = models.CharField(max_length=13)
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
    date_paid = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'tickets'
        managed = False

    def __str__(self):
        return f"{self.kind} -- {self.purchaser}"

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

    def has_active_name_changes(self):
        return self.name_changes.filter(has_paid=False).count() > 0

    @property
    def price(self):
        sum_extras = 0
        for extra in self.extras.all():
            sum_extras = extra.price
        return sum_extras + self.kind.price


class NameChange(models.Model):
    new_name = models.CharField(max_length=100)
    new_email = models.EmailField()
    ticket = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, related_name='name_changes'
    )
    has_paid = models.BooleanField(default=False)
    payment_ref = models.CharField(max_length=13)
    date_requested = models.DateTimeField(auto_now_add=True)
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='name_changes'
    )

    def __str__(self):
        return self.payment_ref

    class Meta:
        managed = False


class Attendance(models.Model):
    ticket = models.OneToOneField(
        Ticket, on_delete=models.CASCADE, related_name='attendance'
    )
    date = models.DateTimeField(auto_now_add=True)
    checker = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='attendances', null=True
    )
