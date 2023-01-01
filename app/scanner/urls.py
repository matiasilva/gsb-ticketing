from django.contrib.flatpages import views as flatpage_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('scan/', views.scan, name='scan'),
    path('checkin/', views.checkin, name='checkin'),
]
