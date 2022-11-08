from django.contrib.auth import BACKEND_SESSION_KEY


def ticketing(request):
    return {"auth_backend": request.session[BACKEND_SESSION_KEY]}
