from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models

from .enums import UserAuthType


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


class PaymentMethod(models.Model):
    enum = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    objects = PaymentMethodManager()

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

    objects = TicketKindManager()

    class Meta:
        db_table = 'ticketkinds'

    def __str__(self):
        return f"{self.enum}"

    def is_available(self):
        return self.allocation.available()


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


class User(AbstractUser):
    # see https://docs.djangoproject.com/en/4.1/ref/contrib/auth/#fields
    # fields inherited: username, first name, last name, email, password,
    # groups, user_permissions, is_staff, is_active, is_superuser, last_login
    # date_joined

    # hard-coded..yikes!
    kind = models.ForeignKey(
        UserKind, on_delete=models.CASCADE, related_name='users', default=5
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
        return self.tickets.filter(is_own=True).count() == 0

    def can_buy_tickets(self, wave):
        return wave.user_kinds.all().filter(pk=self.kind.pk).exists()

    def get_valid_ticketkinds(self, wave):
        # first, retrieve all valid ticketkinds for this userkind
        if any(self.kind.ticket_kinds.values_list('requires_first', flat=True)):
            tickets_qs = self.kind.ticket_kinds.filter(
                requires_first=self.is_first_own_ticket()
            )
        else:
            tickets_qs = self.kind.ticket_kinds.all().order_by('-price')

        # lastly, remove any explicitly hidden tickets
        tickets_qs = tickets_qs.filter(allocation__is_visible=True)

        # lastly, mask out any ticketkinds not allowed in this wave
        # hack around limitations of intersection filtering
        return tickets_qs.filter(
            id__in=wave.ticket_kinds.all().values_list('id', flat=True)
        )

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


class Setting(models.Model):

    current_wave = models.OneToOneField(Wave, on_delete=models.CASCADE)

    # TODO: ensure only a single instance
