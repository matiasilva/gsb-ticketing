# Generated by Django 4.1 on 2022-12-28 14:15

import django.db.models.deletion
import ticketing.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ticketing", "0002_alter_ticket_date_paid"),
    ]

    operations = [
        migrations.CreateModel(
            name="NameChange",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("new_name", models.CharField(max_length=100)),
                ("new_email", models.EmailField(max_length=254)),
                ("has_paid", models.BooleanField(default=False)),
                (
                    "payment_ref",
                    models.CharField(
                        default=ticketing.models.gen_namechange_id, max_length=13
                    ),
                ),
                ("date_requested", models.DateTimeField(auto_now_add=True)),
                (
                    "purchaser",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="name_changes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "ticket",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="name_changes",
                        to="ticketing.ticket",
                    ),
                ),
            ],
        ),
    ]
