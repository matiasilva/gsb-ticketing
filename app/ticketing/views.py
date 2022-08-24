from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return render(request, "index.html")

def login(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def signup(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def manage(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def purchase(request):
    return HttpResponse("Hello, world. You're at the polls index.")