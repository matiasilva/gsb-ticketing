from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as UserAdminOriginal
from django.contrib.auth.models import Group
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import (
    AllowedUser,
    PromoCode,
    Setting,
    Ticket,
    TicketAllocation,
    TicketExtra,
    TicketKind,
    User,
    UserKind,
    Wave,
)


class UserAdmin(UserAdminOriginal):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "tickets_bought",
        "kind",
    )
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
        ("Custom fields", {"fields": ("kind", "has_signed_up")}),
    )

    @admin.display(description='Tickets bought')
    def tickets_bought(self, obj):
        return obj.tickets.count()


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


class TicketExtraAdmin(admin.ModelAdmin):
    list_display = ("name", "tickets_bought")

    @admin.display(description='Extras bought')
    def tickets_bought(self, obj):
        return obj.tickets.count()


class TicketAdmin(admin.ModelAdmin):

    search_fields = ['name', 'uuid']
    list_display = (
        "purchaser",
        "name",
        "kind",
        "has_paid",
        "payment_method",
        "email",
    )
    actions = ['send_confirmation', 'send_payment_confirmation']

    @admin.display(description='Donated', boolean=True)
    def has_donated(self, obj):
        if obj.kind.enum == 'S_ALUM' or obj.kind.enum == 'QJ_ALUM':
            try:
                obj.extras.get(enum="ALUM_DONATION")
                return True
            except ObjectDoesNotExist:
                return False
        else:
            return None

    @admin.action(description='Send confirmation email')
    def send_confirmation(self, request, queryset):
        for ticket in queryset:
            msg = render_to_string("emails/buy.txt", {"ticket": ticket})
            recipients = [ticket.email]
            # both purchaser and attendee should receive email
            if not ticket.is_own:
                recipients.append(ticket.purchaser.email)
            send_mail(
                'GSB23 Ticketing: Ticket Confirmation',
                msg,
                'it@girtonball.com',
                recipients,
            )
        self.message_user(
            request,
            f'{queryset.count()} emails were successfully sent.',
            messages.SUCCESS,
        )

    @admin.action(description='Send payment confirm email')
    def send_payment_confirmation(self, request, queryset):
        for ticket in queryset:
            msg = render_to_string("emails/confirm.txt", {"ticket": ticket})
            recipients = [ticket.email]
            # both purchaser and attendee should receive email
            if not ticket.is_own:
                recipients.append(ticket.purchaser.email)
            send_mail(
                'GSB23 Ticketing: Payment Cleared',
                msg,
                'it@girtonball.com',
                recipients,
            )
        self.message_user(
            request,
            f'{queryset.count()} emails were successfully sent.',
            messages.SUCCESS,
        )


class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ("enum", "description")


class AllowedUserAdmin(admin.ModelAdmin):
    list_display = ("userkind_enum", "username")


admin.site.register(User, UserAdmin)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketKind, TicketKindAdmin)
admin.site.register(Setting)
admin.site.register(Wave)
admin.site.register(AllowedUser, AllowedUserAdmin)
admin.site.register(UserKind, UserKindAdmin)
admin.site.register(TicketAllocation)
admin.site.register(PromoCode, PromoCodeAdmin)
admin.site.register(TicketExtra, TicketExtraAdmin)

admin.site.unregister(Group)
admin.site.unregister(FlatPage)
admin.site.unregister(Site)
