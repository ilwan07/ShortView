from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("auth/register/", views.register, name="register"),
    path("auth/login/", views.loginpage, name="loginpage"),
    path("auth/logout/", views.logoutpage, name="logoutpage"),
    path("preferences/", views.preferences, name="preferences"),
    path("info/passwords/", views.password_info, name="password_info"),
    path("link/new/", views.new_link, name="new_link"),
    path("link/<int:link_id>/", views.redirect_link, name="redirect_link"),
    path("link/<int:link_id>/view/", views.view_link, name="view_link"),
    path("link/<int:link_id>/delete/", views.delete_link, name="delete_link"),
    path("link/<int:link_id>/view/tracker/<int:tracker_id>/", views.view_tracker, name="view_tracker"),
]
