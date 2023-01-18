from datetime import date

import requests
from django.contrib import messages
from django.contrib.auth import BACKEND_SESSION_KEY, authenticate, login, logout
from django.core.mail import mail_admins, send_mail
from django.http import Http404, HttpResponse, QueryDict
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from .forms import (
    BuyTicketForm,
    GuestLoginForm,
    GuestSignupForm,
    NameChangeForm,
    SignupForm,
)
from .models import (
    AllowedUser,
    NameChange,
    Setting,
    Ticket,
    TicketAllocation,
    TicketExtra,
    TicketKind,
    User,
    UserKind,
)
from .utils import login_required, match_identity, validate_ticket_ref


def index(request):
    settings = Setting.objects.get(pk=1)
    wave = settings.current_wave
    if wave.enum == 'INTERNAL':
        return render(request, "bepatient.html", {"title": "Home"})
    else:
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
            allowed_user = AllowedUser.objects.filter(
                username=form.cleaned_data['email']
            )
            if allowed_user.exists():
                userkind = UserKind.objects.get(enum=allowed_user.first().userkind_enum)
            else:
                userkind = UserKind.objects.get(enum='GIRTON_ALUM')
            User.objects.create_user(
                form.cleaned_data['email'],
                form.cleaned_data['passphrase'],
                pname=form.cleaned_data['pname'],
                psurname=form.cleaned_data['psurname'],
                matriculation_date=form.cleaned_data['matric_date'],
                first_name=form.cleaned_data['name'],
                last_name=form.cleaned_data['surname'],
                kind=userkind,
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
        try:
            lookup_res = requests.get(
                'https://mw781.user.srcf.net/lookup-gsb.cgi',
                params={"user": user.username},
                timeout=10,
            )
            lookup_res = lookup_res.json()
        except:
            lookup_res = {}
        status = match_identity(user, lookup_res)

        # db
        user.kind = status
        user.save()

        # this is non-ideal, but it's a reasonable compromise
        visible_name = lookup_res.get('visibleName', "")
        if visible_name == "":
            name = ""
            surname = ""
        else:
            split_name = visible_name.split(' ', 1)
            name = split_name[0]
            surname = split_name[1]
        # don't guess email if they're an alum
        email = f'{user.username}@cam.ac.uk' if not user.profile.raven_for_life else ''
        form = SignupForm(
            initial={
                "status": user.kind.name,
                "name": name,
                "surname": surname,
                "email": email,
            },
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
        if user.has_firstonly_ticketkinds() and user.is_first_own_ticket():
            # fill in name and email as disabled form fields are not sent
            req_post.update({'full_name': user.get_full_name(), 'email': user.email})
        # only handle active tickets from now on
        form = BuyTicketForm(tickets_qs, req_post)
        if form.is_valid():
            ticket = Ticket(
                purchaser=user,
                name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                is_own=(
                    user.has_firstonly_ticketkinds() and user.is_first_own_ticket()
                ),
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


@login_required
def buy_change(request, ref=None):
    # no ticket ref provided
    if ref is None:
        messages.add_message(
            request,
            messages.WARNING,
            'No ticket reference provided!',
        )
        return redirect('manage')

    # validate ticket ref
    if validate_ticket_ref(ref) is None:
        messages.add_message(
            request,
            messages.WARNING,
            'Nonexistent ticket reference provided!',
        )
        return redirect('manage')

    try:
        ticket = Ticket.objects.get(uuid=ref)
    except Ticket.DoesNotExist:
        messages.add_message(
            request,
            messages.WARNING,
            'Nonexistent ticket reference provided!',
        )
        return redirect('manage')

    # ensure ticket belongs to this user
    has_bought_ticket = ticket in request.user.tickets.all()
    if not has_bought_ticket:
        messages.add_message(
            request,
            messages.ERROR,
            'You tried to mess with our platform, violating the terms and conditions in the process. Your account has been reported and appropriate action will be taken.',
        )
        msg = render_to_string(
            "emails/violation.txt",
            {
                "user": request.user,
                "violation": "use ticket reference that was not theirs",
            },
        )
        mail_admins('User TC violation', msg, fail_silently=False)
        return redirect('manage')

    # ensure ticket is a guest ticket (now that we now ticket belongs to user)
    if ticket.is_own:
        messages.add_message(
            request,
            messages.WARNING,
            "You can't change the name on your own ticket!",
        )
        return redirect('manage')

    # check name change is already in progress
    if ticket.has_active_name_changes():
        messages.add_message(
            request,
            messages.WARNING,
            'A name change request is already in progress. Please follow the payment instructions sent by email.',
        )
        return redirect('manage')

    if request.method == 'POST':
        form = NameChangeForm(request.POST)
        if form.is_valid():
            name_change = NameChange(
                new_name=form.cleaned_data['new_name'],
                new_email=form.cleaned_data['new_email'],
                ticket=ticket,
                purchaser=request.user,
            )
            name_change.save()

            msg = render_to_string(
                "emails/name_change.txt", {"nc": name_change, "ticket": ticket}
            )
            recipients = [name_change.new_email, ticket.purchaser.email]
            send_mail(
                'GSB23 Ticketing: Name Change Request',
                msg,
                'it@girtonball.com',
                recipients,
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                'Name change successfully requested. Please check your email for payment details.',
            )
        else:
            return render(
                request,
                "name_change.html",
                {"title": "Name change", "form": form, "ticket": ticket},
            )
        return redirect('manage')

    elif request.method == 'GET':
        # no ticket ref provided
        form = NameChangeForm()
        return render(
            request,
            'name_change.html',
            {"title": "Name change", "form": form, "ticket": ticket},
        )


def patience(request):
    return render(request, "bepatient.html", {"title": "Patience"})


def server_error(request, exception=None):
    return render(request, "errors/500.html", {}, status=500)


def page_not_found(request, exception):
    return render(request, "errors/404.html", {}, status=404)
