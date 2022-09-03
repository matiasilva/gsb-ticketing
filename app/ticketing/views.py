from django.http import HttpResponse
from django.shortcuts import render


def index(request):

    return render(request, "index.html")


def signup(request):
    if not request.user.is_authenticated:
        return redirect('raven_login')
    print(request.user)


def manage(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def purchase(request):
    return HttpResponse("Hello, world. You're at the polls index.")
