from django.http import HttpResponse
from django.shortcuts import render

from .utils import login_required


def index(request):

    return render(request, "index.html")


def signup(request):
    return HttpResponse("Hello, world. You're at the signup index.")


@login_required
def manage(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def purchase(request):
    return HttpResponse("Hello, world. You're at the polls index.")
