import requests
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .enums import UserStatus
from .forms import SignupForm
from .utils import login_required, match_identity


def index(request):

    return render(request, "index.html", {"title": "Home"})


@login_required
def signup(request):
    # aliases
    user = request.user

    # in case a cheeky user tries to sign up twice
    if user.has_signed_up:
        return redirect('manage')

    if request.method == 'POST':
        status = UserStatus(request.user.status)
        form = SignupForm(request.POST, initial={"status": status.label})
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
        status = match_identity(lookup_res, UserStatus, user.profile.raven_for_life)

        # db
        user.status = status
        user.save()

        # this is non-ideal, but it's a reasonable compromise
        split_name = lookup_res['visibleName'].split(' ', 1)
        # don't guess email if they're an alum
        email = f'{user.username}@cam.ac.uk' if not user.profile.raven_for_life else ''
        form = SignupForm(
            {"name": split_name[0], "surname": split_name[1], "email": email},
            initial={"status": user.get_status_display()},
            auto_id='signup_%s',
        )

        return render(request, "signup.html", {"title": "Signup", "form": form})


@login_required
def manage(request):
    user = request.user
    context = {
        "title": "Manage",
        "tickets_remaining": user.get_ticket_allowance() - len(user.tickets.all()),
        "ticket_allowance": user.get_ticket_allowance(),
    }
    return render(request, "manage.html", context)


def buy_ticket(request):
    if request.method == 'POST':
        pass
    else:
        return render(request, "buy_ticket.html", {"title": "Buy"})


def buy_change(request):
    pass
