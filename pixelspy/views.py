from django.shortcuts import redirect, render
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.utils.datastructures import MultiValueDictKeyError


# Create your views here.
def index(request: HttpRequest):
    """
    the view to be displayed when requesting the pixelspy index page
    """
    if request.user.is_authenticated:
        return redirect("home")
    else:
        return render(request, "pixelspy/index.html")


def loginpage(request: HttpRequest):
    """
    the login page, only show if the user isn't logged in, manages the login procedure too
    """
    if request.user.is_authenticated:
        return redirect("home")
    
    try:
        username = request.POST["username"]
        password = request.POST["password"]
    except MultiValueDictKeyError:
        # if no POST data has been received (the user wants the login page)
        return render(request, "pixelspy/login.html")
    
    else:
        # if POST data has been received to try a login
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "pixelspy/login.html", {"error": "The credentials are invalid, make sure the user exists ans the password is correct.",
                                                           "username": username})


def logoutpage(request: HttpRequest):
    """
    logs out the current user
    """
    logout(request)
    return redirect("index")


def home(request: HttpRequest):
    """
    the view for the user home page, only show if user logged in, else redirect to login page
    """
    if not request.user.is_authenticated:
        return redirect("loginpage")
    
    context = {"user": request.user, "pixels": request.user.pixel_set.all()}
    return render(request, "pixelspy/home.html", context)
