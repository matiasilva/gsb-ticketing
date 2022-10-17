from datetime import date

import requests
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import BuyTicketForm, ManualLoginForm, SignupForm
from .models import Setting, Ticket, TicketAllocation, TicketKind, UserKind
from .utils import login_required, match_identity


def index(request):
    return render(request, "index.html", {"title": "Home"})


def privacy(request):
    return render(request, "privacy.html")


def terms(request):
    return render(request, "terms.html")


def login_manual(request):
    user = request.user

    if request.method == 'POST':
        if user.is_authenticated:
            return redirect('manage')

    else:
        return render(request, "login_manual.html", {"form": ManualLoginForm()})


@login_required
def signup(request):
    # aliases
    user = request.user

    # in case a cheeky user tries to sign up twice
    if user.has_signed_up:
        return redirect('manage')

    if request.method == 'POST':
        status = request.user.kind
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
            params={"user": request.user.username},
        )
        lookup_res = lookup_res.json()
        status = match_identity(lookup_res, user.profile.raven_for_life)

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
                dob=form.cleaned_data['dob'],
                is_own=user.is_first_own_ticket(),
                kind=form.cleaned_data['kind'],
                payment_method=user.kind.payment_method,
            )
            allocation = ticket.kind.allocation
            if ticket.kind.is_available():
                ticket.save()
                if allocation.count() == allocation.quantity:
                    # disable ticket allocation once max limit has been reached
                    allocation.is_active = False
                    allocation.save()
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

        form = BuyTicketForm(tickets_qs, initial=initial, auto_id='buy_ticket_%s')
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
