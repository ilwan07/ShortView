from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("login/", views.loginpage, name="loginpage"),
    path("login/check/", views.logincheck, name="logincheck"),
]
