from django.urls import include, path

from . import views

urlpatterns = [
    path('manage/', views.manage, name='manage'),
    path('purchase/', views.purchase, name='purchase'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('', views.index, name='index'),
]