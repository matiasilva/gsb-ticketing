from datetime import date

import requests
from django.contrib import messages
from django.contrib.auth import BACKEND_SESSION_KEY, authenticate, login, logout
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from .forms import BuyTicketForm, GuestLoginForm, GuestSignupForm, SignupForm
from .models import (
    Setting,
    Ticket,
    TicketAllocation,
    TicketExtra,
    TicketKind,
    User,
    UserKind,
)
from .utils import login_required, match_identity


def index(request):
    return render(request, "index.html", {"title": "Home"})


def logout_all(request):
    if request.user.is_authenticated:
        backend = request.session[BACKEND_SESSION_KEY]
        if backend == 'django.contrib.auth.backends.ModelBackend':
            return redirect('logout_guest')
        else:
            return redirect('raven_logout')
    else:
        raise Http404("Stop looking there.")


# POST only
def login_guest(request):
    if request.method == 'POST':
        # in case a logged-in user tries to log in
        if request.user.is_authenticated:
            messages.add_message(
                request,
                messages.WARNING,
                'You\'re already logged in!',
            )
            return redirect('manage')

        form = GuestLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['email'],
                password=form.cleaned_data['passphrase'],
            )
            if user is not None:
                login(request, user)
                return redirect('manage')
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'You entered invalid login details',
                )

        # if invalid data, or wrong pass/username
        return render(
            request,
            "login_manual.html",
            {
                "title": "Alumni Portal",
                "login_form": form,
                "signup_form": GuestSignupForm(),
            },
        )
    else:
        raise Http404("Stop looking there.")


def logout_guest(request):
    logout(request)
    messages.add_message(
        request,
        messages.SUCCESS,
        'You have been successfully logged out.',
    )
    return redirect('index')


# POST only
def signup_guest(request):
    user = request.user

    if request.method == 'POST':
        # in case a logged-in user tries to sign up
        if user.is_authenticated:
            messages.add_message(
                request,
                messages.WARNING,
                'You already have an account!',
            )
            return redirect('manage')

        # only new users here
        form = GuestSignupForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                form.cleaned_data['email'],
                form.cleaned_data['passphrase'],
                pname=form.cleaned_data['pname'],
                psurname=form.cleaned_data['psurname'],
                matriculation_date=form.cleaned_data['matric_date'],
                first_name=form.cleaned_data['name'],
                last_name=form.cleaned_data['surname'],
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'You can now log in with your details on the left.',
            )
            return redirect('guest_portal')
        else:
            return render(
                request,
                "login_manual.html",
                {
                    "title": "Alumni Portal",
                    "login_form": GuestLoginForm(),
                    "signup_form": form,
                },
            )

    else:
        raise Http404("Stop looking there.")


def guest_portal(request):
    user = request.user

    return render(
        request,
        "login_manual.html",
        {
            "title": "Alumni Portal",
            "login_form": GuestLoginForm(),
            "signup_form": GuestSignupForm(),
        },
    )
    pass


@login_required
def signup(request):
    # aliases
    user = request.user

    # in case a cheeky user tries to sign up twice
    if user.has_signed_up:
        return redirect('manage')

    if request.method == 'POST':
        status = user.kind
        form = SignupForm(request.POST, initial={"status": status.name})
        if form.is_valid():
            user.first_name = form.cleaned_data['name']
            user.last_name = form.cleaned_data['surname']
            user.email = form.cleaned_data['email']
            user.has_signed_up = True
            user.save()
            return redirect('manage')
        else:
            return render(request, "signup.html", {"title": "Signup", "form": form})
    else:
        lookup_res = requests.get(
            'https://mw781.user.srcf.net/lookup-gsb.cgi',
            params={"user": user.username},
        )
        lookup_res = lookup_res.json()
        status = match_identity(user, lookup_res)

        # db
        user.kind = status
        user.save()

        # this is non-ideal, but it's a reasonable compromise
        split_name = lookup_res['visibleName'].split(' ', 1)
        # don't guess email if they're an alum
        email = f'{user.username}@cam.ac.uk' if not user.profile.raven_for_life else ''
        form = SignupForm(
            {"name": split_name[0], "surname": split_name[1], "email": email},
            initial={"status": user.kind.name},
            auto_id='signup_%s',
        )

        return render(request, "signup.html", {"title": "Signup", "form": form})


@login_required
def manage(request):
    user = request.user
    settings = Setting.objects.get(pk=1)
    wave = settings.current_wave

    eligible = user.can_buy_tickets(wave) and (user.tickets_left > 0)
    return render(
        request,
        'manage.html',
        {
            "title": "Manage",
            "tickets_left": user.tickets_left,
            "eligible": eligible,
            "wave": wave,
        },
    )


@login_required
def buy_ticket(request):
    # aliases
    user = request.user
    settings = Setting.objects.get(pk=1)
    wave = settings.current_wave

    # eligibility check
    if not user.can_buy_tickets(wave):
        messages.add_message(
            request,
            messages.WARNING,
            'You are not allowed to purchase a ticket in this wave.',
        )
        return redirect('manage')

    if user.tickets_left <= 0:
        messages.add_message(
            request,
            messages.WARNING,
            'You have reached the limit of your ticket allowance.',
        )
        return redirect('manage')

    tickets_qs = user.get_available_ticketkinds(wave)

    # double list comprehension, bonkers!
    # all_extras = [extra for extras in tickets_qs for extra in extras]
    # note last value wins
    # unique_extras = {extra.enum: extra for extra in extras}

    if not tickets_qs.exists():
        messages.add_message(
            request,
            messages.WARNING,
            'There are no valid ticket types for you to buy in this wave.',
        )
        return redirect('manage')

    if request.method == 'POST':

        req_post = request.POST.copy()
        if user.is_first_own_ticket():
            # fill in name and email as disabled form fields are not sent
            req_post.update({'full_name': user.get_full_name(), 'email': user.email})
        # only handle active tickets from now on
        form = BuyTicketForm(tickets_qs, req_post)
        if form.is_valid():
            ticket = Ticket(
                purchaser=user,
                name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                is_own=user.is_first_own_ticket(),
                kind=form.cleaned_data['kind'],
                is_veg=form.cleaned_data['is_veg'],
                is_alc=form.cleaned_data['is_alc'],
                payment_method=user.kind.payment_method,
            )
            allocation = ticket.kind.allocation
            if ticket.kind.is_available():
                ticket.save()

                # hardcoded extras
                alum_donation_extra = form.cleaned_data.get(
                    f'alum_donation_{ticket.kind.pk}'
                )
                if alum_donation_extra:
                    ticket.extras.add(TicketExtra.objects.get(enum='ALUM_DONATION'))

                alum_joint_extra = form.cleaned_data.get(f'alum_joint_{ticket.kind.pk}')
                if alum_joint_extra:
                    ticket.extras.add(TicketExtra.objects.get(enum='ALUM_JOINT'))

                if allocation.count() == allocation.quantity:
                    # disable ticket allocation once max limit has been reached
                    allocation.is_active = False
                    allocation.save()

                # send confirmation email
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
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    'That ticket type has sold out!',
                )
            return redirect('manage')
        else:
            return render(
                request,
                "buy_ticket.html",
                {
                    "title": "Buy",
                    "form": form,
                    "valid_ticketkinds": user.get_valid_ticketkinds(wave),
                },
            )
    else:
        if user.is_first_own_ticket():
            initial = {
                "full_name": user.get_full_name(),
                "email": user.email,
            }
        else:
            initial = dict()

        form = BuyTicketForm(tickets_qs, initial=initial)
        return render(
            request,
            "buy_ticket.html",
            {
                "title": "Buy",
                "form": form,
                "valid_ticketkinds": user.get_valid_ticketkinds(wave),
            },
        )


def buy_change(request):
    pass
