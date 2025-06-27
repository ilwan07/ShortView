from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError

from .models import Pixel, Tracker


# Create your views here.
def index(request: HttpRequest):
    """
    the view to display the index page, or the home page if the user is logged in
    """
    if not request.user.is_authenticated:
        return render(request, "pixelspy/index.html")
    
    else:
        context = {"user": request.user, "pixels": request.user.pixel_set.all()}
        return render(request, "pixelspy/home.html", context)


def loginpage(request: HttpRequest):
    """
    the login page, only show if the user isn't logged in, manages the login procedure too
    """
    if request.user.is_authenticated:
        return redirect("index")
    
    try:
        identifier = request.POST["identifier"]
        password = request.POST["password"]
    except MultiValueDictKeyError:
        # if no POST data has been received (the user wants the login page)
        return render(request, "pixelspy/login.html")
    
    else:
        # if POST data has been received to try a login
        login_type = "email" if "@" in identifier else "username"
        try:
            if login_type == "email":
                identifier = identifier.lower()  # emails are case insensitive, so standarize everything to lowercase
                user_object = User.objects.get(email=identifier)
            else:
                user_object = User.objects.get(username=identifier)
        except User.DoesNotExist:
            # if the identifier is wrong
            return render(request, "pixelspy/login.html", {"error": f"The {login_type} you entered is invalid. Make sure the {login_type} is correct, or use the sign in button to create a new account.",
                                                           "identifier": identifier})
        except User.MultipleObjectsReturned:
            # if there (somehow) is multiple users possible
            return render(request, "pixelspy/login.html", {"error": f"Multiple different users are using this {login_type}. This is an issue, please contact the developper to fix this.",
                                                           "identifier": identifier})
        
        # log the user in if everything is ok
        username = user_object.username
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            return render(request, "pixelspy/login.html", {"error": "The credentials are invalid, make sure that the password is correct.",
                                                           "identifier": identifier})


def password_info(request: HttpRequest):
    """
    an informative page to explain to the user how passwords are stored
    """
    return render(request, "pixelspy/info/passwords.html")


def logoutpage(request: HttpRequest):
    """
    logs out the current user
    """
    logout(request)
    return redirect("index")

def view_pixel(request: HttpRequest, pixel_id: int):
    """
    displays info about a pixel, if it belongs to the active user
    """
    if not request.user.is_authenticated:
        return redirect("loginpage")
    try:
        pixelObject = Pixel.objects.get(id=pixel_id)
    except Pixel.DoesNotExist:
        raise Http404("Pixel does not exist")
    else:
        if pixelObject.owner == request.user:
            return render(request, "pixelspy/view_pixel.html", {"pixel": pixelObject})
        else:
            raise PermissionDenied("You are not the owner of this pixel")

def view_tracker(request: HttpRequest, pixel_id: int, tracker_id: int):
    """
    displays the data from a tracker if it exists and comes from the correct pixel
    the use of a pixel id too is for ease of navigation with the url structure
    """
    return HttpResponse("<h1>TODO</h1>")  #TODO
