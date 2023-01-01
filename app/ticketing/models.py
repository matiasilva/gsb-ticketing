import random
from datetime import date

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


def gen_random_id(prefix):
    return (
        f"{prefix}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789', k=8))}"
    )


def gen_ticket_id():
    return gen_random_id('GSB')


def gen_namechange_id():
    return gen_random_id('GSBNC')


class AllowedUserManager(models.Manager):
    def get_by_natural_key(self, username):
        return self.get(username=username)


class PaymentMethodManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class TicketKindManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class UserKindManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class WaveManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class TicketAllocationManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class TicketExtraManager(models.Manager):
    def get_by_natural_key(self, enum):
        return self.get(enum=enum)


class PaymentMethod(models.Model):
    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    objects = PaymentMethodManager()

    def __str__(self):
        return self.name


class TicketExtra(models.Model):
    enum = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    label = models.CharField(max_length=100)
    opt_out = models.BooleanField()

    objects = TicketExtraManager()

    def __str__(self):
        return self.name


class TicketAllocation(models.Model):

    enum = models.CharField(max_length=20, unique=True)
    quantity = models.IntegerField()
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_visible = models.BooleanField(default=True)

    objects = TicketAllocationManager()

    def __str__(self):
        return self.name

    def count(self):
        return Ticket.objects.filter(kind__allocation__pk=self.pk).count()

    def is_available(self):
        return self.count() < self.quantity


class TicketKind(models.Model):

    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    requires_first = models.BooleanField(default=False)
    allocation = models.ForeignKey(
        TicketAllocation, on_delete=models.CASCADE, related_name='kinds'
    )
    optional_extras = models.ManyToManyField(
        TicketExtra, related_name='kinds', blank=True
    )

    objects = TicketKindManager()

    class Meta:
        db_table = 'ticketkinds'

    def __str__(self):
        return f"{self.enum}"

    def is_available(self):
        return self.allocation.is_available()


class UserKind(models.Model):
    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    # ideally make this many-to-many relation
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, related_name='userkinds'
    )
    allowance = models.IntegerField()
    ticket_kinds = models.ManyToManyField(TicketKind, db_table="userkind_ticketkinds")

    objects = UserKindManager()

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password,
        pname=None,
        psurname=None,
        matriculation_date=None,
        first_name=None,
        last_name=None,
        kind=UserKind.objects.get(enum='GIRTON_ALUM'),
    ):
        user = self.model(
            username=email,
            email=email,
            pname=pname,
            psurname=psurname,
            matriculation_date=matriculation_date,
            first_name=first_name,
            last_name=last_name,
            has_signed_up=True,
            kind=kind,
        )
        user.set_password(password)
        user.save()
        return user


class User(AbstractUser):
    # see https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#fields
    # fields inherited: username, first name, last name, email, password,
    # groups, user_permissions, is_staff, is_active, is_superuser, last_login
    # date_joined

    # hard-coded..yikes!
    kind = models.ForeignKey(
        UserKind, on_delete=models.CASCADE, related_name='users', default=5
    )

    has_signed_up = models.BooleanField(default=False)

    # optional fields
    matriculation_date = models.DateField(null=True)
    pname = models.CharField(max_length=100)
    psurname = models.CharField(max_length=100)

    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_first_own_ticket(self):
        return self.tickets.filter(is_own=True).count() == 0

    def can_buy_tickets(self, wave):
        return wave.user_kinds.all().filter(pk=self.kind.pk).exists()

    def has_firstonly_ticketkinds(self):
        return any(self.kind.ticket_kinds.values_list('requires_first', flat=True))

    def get_valid_ticketkinds(self, wave):
        # note: this method obtains all the valid (but not necessarily purchasable) ticket types
        # use only for displaying readonly information, never for transactions

        # first, retrieve all valid ticketkinds for this userkind
        if self.has_firstonly_ticketkinds():
            tickets_qs = self.kind.ticket_kinds.filter(
                requires_first=self.is_first_own_ticket()
            )
        else:
            tickets_qs = self.kind.ticket_kinds.all()

        tickets_qs = tickets_qs.filter(allocation__is_visible=True)

        # secondly, mask out any ticketkinds not allowed in this wave
        # hack around limitations of intersection filtering
        return tickets_qs.filter(
            id__in=wave.ticket_kinds.all().values_list('id', flat=True)
        ).order_by('-price')

    def get_available_ticketkinds(self, wave):
        # return the ticketkinds available NOW to the user
        tickets_qs = self.get_valid_ticketkinds(wave)
        # remove any explicitly hidden or disabled tickets
        return tickets_qs.filter(allocation__is_active=True).all()

    @property
    def tickets_left(self):
        return self.kind.allowance - len(self.tickets.all())


class Ticket(models.Model):
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='tickets'
    )

    # attendee details
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)

    # internal
    is_own = models.BooleanField()
    uuid = models.CharField(max_length=13, default=gen_ticket_id)
    date_applied = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True)

    # ticket type
    kind = models.ForeignKey(
        TicketKind, on_delete=models.CASCADE, related_name='tickets'
    )
    extras = models.ManyToManyField(TicketExtra, related_name='tickets', blank=True)

    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, related_name='tickets'
    )
    has_paid = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True, blank=True)

    is_veg = models.BooleanField(default=False)
    is_alc = models.BooleanField(default=False)

    class Meta:
        db_table = 'tickets'
        constraints = [
            models.UniqueConstraint(
                fields=['purchaser'],
                condition=models.Q(is_own=True),
                name='unique_own_ticket_user',
            ),
        ]

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
    payment_ref = models.CharField(max_length=13, default=gen_namechange_id)
    date_requested = models.DateTimeField(auto_now_add=True)
    purchaser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='name_changes'
    )

    def __str__(self):
        return self.payment_ref

    def price(self):
        return TicketKind.objects.get(enum='NAME_CHANGE').price


class PromoCode(models.Model):
    enum = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    value = models.CharField(max_length=30)


class Wave(models.Model):
    enum = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    ticket_kinds = models.ManyToManyField(
        TicketKind, db_table='ticketkinds_waves', related_name='waves'
    )
    user_kinds = models.ManyToManyField(
        UserKind, db_table='userkinds_waves', related_name='waves'
    )

    objects = WaveManager()

    def __str__(self):
        return self.name


class Attendance(models.Model):
    ticket = models.OneToOneField(
        Ticket, on_delete=models.CASCADE, related_name='attendance'
    )
    date = models.DateTimeField(auto_now_add=True)
    checker = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='attendances', null=True
    )


class Setting(models.Model):

    current_wave = models.OneToOneField(Wave, on_delete=models.CASCADE)

    # TODO: ensure only a single instance


class AllowedUser(models.Model):
    # match them to a userkind
    userkind_enum = models.CharField(max_length=30)
    username = models.CharField(max_length=150)

    objects = AllowedUserManager()
