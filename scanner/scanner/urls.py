from django.urls import path

from scanner import views

urlpatterns = [
    path('getticketdata', views.get_ticket_data, name="get_ticket_data"),
    path('checkin', views.checkin, name="checkin"),
    path('setname', views.set_name, name="set_name"),
    path('', views.scanner, name="scanner"),
]
