from django.urls import include, path

from . import views

urlpatterns = [
    path('', include('ucamwebauth.urls')),
    path('manage/', views.manage, name='manage'),
    path('signup/', views.signup, name='signup'),
    path('buy/ticket', views.buy_ticket, name='buy_ticket'),
    path('buy/change', views.buy_change, name='buy_change'),
    path('buy/', views.buy_ticket, name='buy_ticket'),
    path('', views.index, name='index'),
]
