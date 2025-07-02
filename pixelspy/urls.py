from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.loginpage, name="loginpage"),
    path("auth/logout/", views.logoutpage, name="logoutpage"),
    path("preferences/", views.preferences, name="preferences"),
    path("info/passwords/", views.password_info, name="password_info"),
    path("pixel/new/", views.new_pixel, name="new_pixel"),
    path("pixel/<int:pixel_id>/", views.view_pixel, name="view_pixel"),
    path("pixel/<int:pixel_id>/image.png", views.display_pixel, name="display_pixel"),
    path("pixel/<int:pixel_id>/tracker/<int:tracker_id>/", views.view_tracker, name="view_tracker"),
]
