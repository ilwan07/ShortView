from django.shortcuts import redirect, render
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError


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


def logoutpage(request: HttpRequest):
    """
    logs out the current user
    """
    logout(request)
    return redirect("index")
