from django.contrib.flatpages import views as flatpage_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('', include('ucamwebauth.urls')),
    path('manage/', views.manage, name='manage'),
    path('signup/', views.signup, name='signup'),
    path('buy/ticket', views.buy_ticket, name='buy_ticket'),
    path('buy/change', views.buy_change, name='buy_change'),
    path('buy/', views.buy_ticket, name='buy_ticket'),
    path('privacy/', flatpage_views.flatpage, {'url': '/privacy/'}, name='privacy'),
    path('terms/', flatpage_views.flatpage, {'url': '/terms/'}, name='terms'),
    path(
        'accounts/request-manual-account/',
        views.request_account,
        name='request_account',
    ),
    path('accounts/login/manual', views.login_manual, name='login_manual'),
    path('', views.index, name='index'),
]
