from django.contrib.flatpages import views as flatpage_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('', include('ucamwebauth.urls')),
    path('accounts/login/guest/', views.login_guest, name='login_guest'),
    path('accounts/logout/guest/', views.logout_guest, name='logout'),
    path('buy/ticket/', views.buy_ticket, name='buy_ticket'),
    path('buy/change/<str:ref>', views.buy_change, name='buy_change'),
    path('buy/', views.buy_ticket, name='buy_ticket'),
    path('download/<str:ref>', views.download_ticket, name='download_ticket'),
    path('guest/', views.guest_portal, name='guest_portal'),
    path('logout/', views.logout_all, name="logout_all"),
    path('manage/', views.manage, name='manage'),
    path('patience/', views.patience, name="patience"),
    path('privacy/', flatpage_views.flatpage, {'url': '/privacy/'}, name='privacy'),
    path('signup/', views.signup, name='signup'),
    path('signup/guest/', views.signup_guest, name='signup_guest'),
    path('terms/', flatpage_views.flatpage, {'url': '/terms/'}, name='terms'),
    path('', views.index, name='index'),
]
