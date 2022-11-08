from django.contrib.flatpages import views as flatpage_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('', include('ucamwebauth.urls')),
    path('manage/', views.manage, name='manage'),
    path('signup/', views.signup, name='signup'),
    path('signup/guest/', views.signup_guest, name='signup_guest'),
    path('buy/ticket/', views.buy_ticket, name='buy_ticket'),
    path('buy/change/', views.buy_change, name='buy_change'),
    path('buy/', views.buy_ticket, name='buy_ticket'),
    path('privacy/', flatpage_views.flatpage, {'url': '/privacy/'}, name='privacy'),
    path('terms/', flatpage_views.flatpage, {'url': '/terms/'}, name='terms'),
    path('guest/', views.guest_portal, name='guest_portal'),
    path('accounts/login/guest/', views.login_guest, name='login_guest'),
    path('accounts/logout/guest/', views.logout_guest, name='logout_guest'),
    path('', views.index, name='index'),
]
