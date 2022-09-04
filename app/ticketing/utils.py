from functools import wraps
from urllib.parse import urlparse

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, resolve_url


def login_required(
    view_func=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='raven_login'
):
    @wraps(view_func)
    def _wrapper_view(request, *args, **kwargs):

        if request.user.is_authenticated:
            # ensure user has entered sign up details before proceeding
            if not request.user.has_signed_up:
                return redirect('signup')
            return view_func(request, *args, **kwargs)

        # logic for guessing next redirect
        path = request.build_absolute_uri()
        resolved_login_url = resolve_url(login_url or settings.LOGIN_URL)
        # If the login url is the same scheme and net location then just
        # use the path as the "next" url.
        login_scheme, login_netloc = urlparse(resolved_login_url)[:2]
        current_scheme, current_netloc = urlparse(path)[:2]
        if (not login_scheme or login_scheme == current_scheme) and (
            not login_netloc or login_netloc == current_netloc
        ):
            path = request.get_full_path()
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(path, resolved_login_url, redirect_field_name)

    return _wrapper_view
