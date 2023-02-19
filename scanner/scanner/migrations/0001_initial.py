# Generated by Django 4.1.7 on 2023-02-19 13:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='NameChange',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('new_name', models.CharField(max_length=100)),
                ('new_email', models.EmailField(max_length=254)),
                ('has_paid', models.BooleanField(default=False)),
                ('payment_ref', models.CharField(max_length=13)),
                ('date_requested', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('enum', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_own', models.BooleanField()),
                ('uuid', models.CharField(max_length=13)),
                ('date_applied', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('has_paid', models.BooleanField(default=False)),
                ('date_paid', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'tickets',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='TicketKind',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('enum', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('price', models.IntegerField()),
                ('requires_first', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'ticketkinds',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('username', models.CharField(max_length=150)),
                ('first_name', models.CharField(max_length=150)),
                ('last_name', models.CharField(max_length=150)),
                ('email', models.EmailField(max_length=254)),
                ('matriculation_date', models.DateField(null=True)),
                ('pname', models.CharField(max_length=100)),
                ('psurname', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UserKind',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('enum', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('date', models.DateTimeField(auto_now_add=True)),
                (
                    'checker',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='attendances',
                        to='scanner.user',
                    ),
                ),
                (
                    'ticket',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='attendance',
                        to='scanner.ticket',
                    ),
                ),
            ],
        ),
    ]
