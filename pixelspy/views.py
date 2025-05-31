from django.shortcuts import redirect, render
from django.http import HttpRequest


# Create your views here.
def index(request: HttpRequest):
    """
    the view to be displayed when requesting the pixelspy index page
    """
    return render(request, "pixelspy/index.html")


def login(request: HttpRequest):
    """
    the login page, only show if the user isn't logged in
    """
    if request.user.is_authenticated:
        return redirect("home")
    
    else:
        return render(request, "pixelspy/login.html")


def home(request: HttpRequest):
    """
    the view for the user home page, only show if user logged in, else redirect to login page
    """
    if not request.user.is_authenticated:
        return redirect("login")
    
    context = {"pixels": None}  #TODO: pass all the user's pixel objects to the context
    return render(request, "pixelspy/home.html", context)
