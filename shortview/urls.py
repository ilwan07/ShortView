from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.loginpage, name="loginpage"),
    path("logout/", views.logoutpage, name="logoutpage"),
    path("info/passwords/", views.password_info, name="password_info"),
    path("info/conditions/", views.conditions, name="conditions"),
    path("preferences/", views.preferences, name="preferences"),
    path("link/new/", views.new_link, name="new_link"),
    path("<int:link_id>/", views.redirect_link, name="redirect_link"),
    path("<int:link_id>/edit/", views.view_link, name="view_link"),
    path("<int:link_id>/delete/", views.delete_link, name="delete_link"),
    path("<int:link_id>/change_notify/", views.link_change_notify, name="link_change_notify"),
    path("<int:link_id>/tracker/<int:tracker_id>/", views.view_tracker, name="view_tracker"),
]
