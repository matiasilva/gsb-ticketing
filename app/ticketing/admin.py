import base64
import json
import os
from datetime import timedelta
from functools import reduce
from operator import or_

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as UserAdminOriginal
from django.contrib.auth.models import Group
from django.contrib.flatpages.models import FlatPage
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from google.cloud import storage
from google.oauth2.service_account import Credentials

from .models import (
    AllowedUser,
    NameChange,
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
        if obj.allocation.quantity != 0:
            return f"{int(100*obj.allocation.count()/obj.allocation.quantity)}%"
        return "0%"


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
    actions = [
        'send_confirmation',
        'send_payment_confirmation',
        'download_ticketing_details',
        'send_payment_confirm',
        'send_download_link',
    ]
    list_per_page = 1200

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(TicketAdmin, self).get_search_results(
            request, queryset, search_term
        )
        search_words = search_term.split()
        if search_words:
            q_objects = [
                Q(**{field + '__icontains': word})
                for field in self.search_fields
                for word in search_words
            ]
            queryset |= self.model.objects.filter(reduce(or_, q_objects))
        return queryset, use_distinct

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
    def send_payment_confirm(self, request, queryset):
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

    @admin.action(description='Make them pay')
    def send_payment_confirmation(self, request, queryset):
        for ticket in queryset:
            msg = render_to_string("emails/reminder.txt", {"ticket": ticket})
            recipients = [ticket.email]
            # both purchaser and attendee should receive email
            if not ticket.is_own:
                recipients.append(ticket.purchaser.email)
            send_mail(
                'GSB23 Ticketing: Payment reminder',
                msg,
                'it@girtonball.com',
                recipients,
            )
        self.message_user(
            request,
            f'{queryset.count()} emails were successfully sent.',
            messages.SUCCESS,
        )

    @admin.action(description='Download as CSV for ticket generation')
    def download_ticketing_details(self, request, queryset):
        import csv
        import io

        from django.http import HttpResponse

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["name", "uuid", "kind"])
        for ticket in queryset:
            writer.writerow([ticket.name, ticket.uuid, ticket.kind])
        buffer.seek(0)
        return HttpResponse(buffer, content_type='text/csv')

    @admin.action(description='Send link to download tickets')
    def send_download_link(self, request, queryset):
        # Google uses JSON files and heroku works with env vars, So base64
        # encoded json env vars is my best compromise to work with both systems
        cred_dict = json.loads(base64.b64decode(os.environ["GOOGLE_BASE_64_CREDS"]))
        creds = Credentials.from_service_account_info(cred_dict)
        client = storage.Client(credentials=creds)
        bucket = client.bucket(os.environ["GOOGLE_BUCKET_NAME"])
        for ticket in queryset:
            blob = bucket.blob(str(ticket.uuid) + ".pdf")
            # Generate a signed URL with the Content-Disposition header set
            url = blob.generate_signed_url(
                response_disposition="attachment;",
                version="v4",
                expiration=timedelta(days=7),
                method="GET",
            )
            msg = render_to_string(
                "emails/link_email.txt", {"url": url, "ticket": ticket}
            )
            recipients = [ticket.email]
            send_mail(
                'GSB23 Ticketing: Download your ticket',
                strip_tags(msg),
                'it@girtonball.com',
                recipients,
                html_message=msg,
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


class NameChangeAdmin(admin.ModelAdmin):

    list_display = (
        "payment_ref",
        "purchaser_username",
        "purchaser_name",
        "new_name",
        "old_name",
        "has_paid",
    )
    search_fields = ['purchaser_username', 'payment_ref']
    raw_id_fields = ("ticket", "purchaser")
    actions = ['mark_completed', 'send_payment_email']

    @admin.display(description='Old name')
    def old_name(self, obj):
        return obj.ticket.name

    @admin.display(description='Purchaser username')
    def purchaser_username(self, obj):
        return obj.purchaser.username

    @admin.display(description='Purchaser name')
    def purchaser_name(self, obj):
        return obj.purchaser.get_full_name()

    @admin.action(description='Mark NC as paid')
    def mark_completed(self, request, queryset):
        for nc in queryset:
            nc.ticket.name = nc.new_name
            nc.ticket.email = nc.new_email
            nc.has_paid = True
            nc.ticket.save()
            nc.save()
        self.message_user(
            request,
            f'{queryset.count()} name changes were successfully actioned and marked paid.',
            messages.SUCCESS,
        )

    @admin.action(description='Send payment email')
    def send_payment_email(self, request, queryset):
        for nc in queryset:
            msg = render_to_string(
                "emails/name_change.txt", {"nc": nc, "ticket": nc.ticket}
            )
            recipients = [nc.new_email, nc.ticket.purchaser.email, nc.ticket.email]
            send_mail(
                'GSB23 Ticketing: Name Change Request',
                msg,
                'it@girtonball.com',
                recipients,
            )
        self.message_user(
            request,
            f'{queryset.count()} name changes were successfully emailed.',
            messages.SUCCESS,
        )


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
admin.site.register(NameChange, NameChangeAdmin)

admin.site.unregister(Group)
admin.site.unregister(FlatPage)
admin.site.unregister(Site)
