from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UserAdminOriginal
from django.contrib.auth.models import Group

from .models import Setting, Ticket, TicketAllocation, TicketKind, User, UserKind


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


class UserKindAdmin(admin.ModelAdmin):
    list_display = ("name", "tickets_bought", "userkind_count")

    @admin.display(description='Tickets bought')
    def tickets_bought(self, obj):
        return Ticket.objects.filter(purchaser__kind=obj).count()

    @admin.display(description='User count')
    def userkind_count(self, obj):
        return User.objects.filter(kind=obj).count()


class TicketKindAdmin(admin.ModelAdmin):
    list_display = ("name", "enum", "tickets_bought", "allocation_qty", "availability")

    @admin.display(description='Tickets bought')
    def tickets_bought(self, obj):
        return Ticket.objects.filter(kind=obj).count()

    @admin.display(description='Allocation')
    def allocation_qty(self, obj):
        return f"{obj.allocation.quantity}"

    @admin.display(description='Availability')
    def availability(self, obj):
        return f"{int(100*obj.allocation.count()/obj.allocation.quantity)}%"


class TicketAdmin(admin.ModelAdmin):
    list_display = ("purchaser", "name", "kind", "has_paid", "payment_method")


admin.site.register(User, UserAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketKind, TicketKindAdmin)
admin.site.register(Setting)
admin.site.register(UserKind, UserKindAdmin)
admin.site.register(TicketAllocation)

admin.site.unregister(Group)
