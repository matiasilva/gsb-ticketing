from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (
    PaymentMethod,
    Setting,
    Ticket,
    TicketAllocation,
    TicketKind,
    User,
    UserKind,
    Wave,
)

admin.site.register(User)
admin.site.register(Ticket)
admin.site.register(Setting)
admin.site.register(UserKind)
admin.site.register(Wave)
admin.site.register(TicketKind)
admin.site.register(TicketAllocation)
admin.site.register(PaymentMethod)

admin.site.unregister(Group)
