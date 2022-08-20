from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def login(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def signup(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def manage(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def purchase(request):
    return HttpResponse("Hello, world. You're at the polls index.")