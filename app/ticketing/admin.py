from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminOriginal
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


class UserAdmin(UserAdminOriginal):
    readonly_fields = ["last_login", "date_joined"]
    fieldsets = (
        (None, {"fields": ("username",)}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Custom fields", {"fields": ("kind",)}),
    )


admin.site.register(User, UserAdmin)
admin.site.register(Ticket)
admin.site.register(Setting)
admin.site.register(UserKind)
admin.site.register(Wave)
admin.site.register(TicketAllocation)
admin.site.register(PaymentMethod)

admin.site.unregister(Group)
