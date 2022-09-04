import requests
from django.http import HttpResponse
from django.shortcuts import render

from .utils import login_required


def index(request):

    return render(request, "index.html")


@login_required
def signup(request):
    lookup_res = requests.get(
        'https://mw781.user.srcf.net/lookup-gsb.cgi',
        params={"user": request.user.username},
    )
    lookup_res = lookup_res.json()
    return render(request, "signup.html", {"title": "Signup"})


@login_required
def manage(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def purchase(request):
    return HttpResponse("Hello, world. You're at the polls index.")
