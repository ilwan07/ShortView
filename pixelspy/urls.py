from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.loginpage, name="loginpage"),
    path("info/passwords", views.passStoreInfo, name="passStoreInfo"),
    path("logout/", views.logoutpage, name="logoutpage"),
]
