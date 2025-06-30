from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.loginpage, name="loginpage"),
    path("logout/", views.logoutpage, name="logoutpage"),
    path("preferences/", views.preferences, name="preferences"),
    path("preferences/submit", views.submit_preferences, name="submit_preferences"),
    path("info/passwords", views.password_info, name="password_info"),
    path("pixel/<int:pixel_id>", views.view_pixel, name="view_pixel"),
    path("pixel/<int:pixel_id>/tracker/<int:tracker_id>", views.view_tracker, name="view_tracker"),
]
