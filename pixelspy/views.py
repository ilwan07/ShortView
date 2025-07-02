from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse, Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User

from .models import Profile, Pixel, Tracker

import datetime
import re

# Create your views here.
def index(request: HttpRequest):
    """
    the view to display the index page, or the home page if the user is logged in
    """
    if not request.user.is_authenticated:
        return render(request, "pixelspy/index.html")
    
    else:
        # make sure the user has a profile
        if not Profile.objects.filter(user=request.user).exists():
            profile = Profile(user=request.user)
            profile.save()
        
        return render(request, "pixelspy/home.html", {"user": request.user,
                                                      "profile": request.user.profile,
                                                      "pixels": request.user.pixel_set.all(),
                                                      })


def preferences(request: HttpRequest):
    """
    the view to let the user change the preferences
    """
    if not request.user.is_authenticated:
        return redirect("loginpage")
    
    # make sure the user has a profile
    if not Profile.objects.filter(user=request.user).exists():
        profile = Profile(user=request.user)
        profile.save()

    profile = request.user.profile
    lifetime: datetime.timedelta = profile.default_lifetime
    hours = lifetime.seconds // 3600
    minutes = (lifetime.seconds % 3600) // 60
    seconds = (lifetime.seconds % 60)
    return render(request, "pixelspy/preferences.html", {"profile": profile,
                                                            "never_expire": request.user.profile.default_lifetime == datetime.timedelta(0),
                                                            "days": lifetime.days, "hours": hours, "minutes": minutes, "seconds": seconds,
                                                            })


def submit_preferences(request: HttpRequest):
    """
    set the new preferences using the POST data from the preferences view
    """
    if not request.user.is_authenticated:
        return redirect("loginpage")
    if "never_expire" in request.POST:
        days, hours, minutes, seconds = 0, 0, 0, 0
    elif all(element in request.POST for element in ["days", "hours", "minutes", "seconds"]):
        days = request.POST["days"]
        hours = request.POST["hours"]
        minutes = request.POST["minutes"]
        seconds = request.POST["seconds"]
    else:
        messages.error(request, "Error: Some data to post is missing, try again or contact the developer to fix the issue.")
        return redirect("preferences")
    
    try:
        days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
    except ValueError:
        messages.error(request, "Error: You tried to set the lifetime value without using integers.")
        return redirect("preferences")
    never_expire = request.POST["never_expire"] == "on" if "never_expire" in request.POST else False
    hide_expired = request.POST["hide_expired"] == "on" if "hide_expired" in request.POST else False
    
    profile:Profile = request.user.profile
    profile.default_lifetime = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    profile.hide_expired = hide_expired
    profile.save()
    messages.success(request, "Successfully applied the new preferences!")
    return redirect("preferences")


def register(request: HttpRequest):
    """
    view with a form to register a new user
    """
    if request.user.is_authenticated:
        return redirect("index")
    
    if all(element in request.POST for element in ["username", "email", "password", "password_confirm"]):
        username = request.POST["username"]
        email = request.POST["email"].lower()  # emails are case insensitive, so standarize everything to lowercase
        password = request.POST["password"]
        password_confirm = request.POST["password_confirm"]
    else:
        # if some POST data hasn't been received (the user wants the register page)
        return render(request, "pixelspy/register.html")
    
    # if POST data has been received to try a registration
    # check username validity
    if not re.fullmatch(r"^[A-Za-z0-9_.+-]{3,50}$", username):
        return render(request, "pixelspy/register.html", {"error": "The username format is invalid, it must be between 3 and 50 characters, can only contain letters, numbers, and these symbols:  _ + . -",
                                                          "username": username,
                                                          "email": email,
                                                          })
    if User.objects.filter(username=username).exists():
        return render(request, "pixelspy/register.html", {"error": "This username already exists, try another one, or use the log in page if your account already exists.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    
    # check email validity
    if not re.fullmatch(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", email):
        return render(request, "pixelspy/register.html", {"error": "The email format is invalid, please enter a valid email address.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    if User.objects.filter(email=email).exists():
        return render(request, "pixelspy/register.html", {"error": "This email address is already in use, try logging in with it.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    
    # check basic password validity
    if password != password_confirm:
        return render(request, "pixelspy/register.html", {"error": "The two passwords you entered are different, you need to enter the same password twice.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    
    # try registering with the given credentials
    try:
        validate_password(password)
    except ValidationError as e:
        # if the password is not valid, return the error message(s)
        return render(request, "pixelspy/register.html", {"error": f"The password you entered is not valid. {' '.join(e.messages)}",
                                                          "username": username,
                                                          "email": email,
                                                          })
    else:
        user = User.objects.create_user(username, email, password)
        profile = Profile(user=user)
        profile.save()
        login(request, user)
        return redirect("index")


def loginpage(request: HttpRequest):
    """
    the login page, only show if the user isn't logged in, manages the login procedure too
    """
    if request.user.is_authenticated:
        return redirect("index")
    
    if all(element in request.POST for element in ["identifier", "password"]):
        identifier = request.POST["identifier"]
        password = request.POST["password"]
    else:
        # if some POST data hasn't been received (the user wants the login page)
        return render(request, "pixelspy/login.html")
    
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
                                                        "identifier": identifier,
                                                        })
    except User.MultipleObjectsReturned:
        # if there (somehow) are multiple users possible
        return render(request, "pixelspy/login.html", {"error": f"Multiple different users are using this {login_type}. This is an issue, please contact the developper to fix this.",
                                                        "identifier": identifier,
                                                        })
    
    # log the user in if everything is ok
    username = user_object.username
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("index")
    else:
        return render(request, "pixelspy/login.html", {"error": "The credentials are invalid, make sure that the password is correct.",
                                                        "identifier": identifier,
                                                        })


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
    # verify that the pixel exists
    try:
        pixelObject = Pixel.objects.get(id=pixel_id)
    except Pixel.DoesNotExist:
        raise Http404("Pixel does not exist")
    else:
        # check that the user owns the pixel, then display the page
        if pixelObject.owner == request.user:
            return render(request, "pixelspy/view_pixel.html", {"pixel": pixelObject,
                                                                "trackers": pixelObject.tracker_set.all(),
                                                                })
        else:
            raise PermissionDenied("You are not the owner of this pixel")


def view_tracker(request: HttpRequest, pixel_id:int, tracker_id:int):
    """
    view the full header of a request to the pixel, also verifies if the url is consistent
    the used url contains the pixel id for the sake of easy url navigation for the user
    """
    if not request.user.is_authenticated:
        return redirect("loginpage")
    # verify that the pixel exists
    try:
        pixelObject = Pixel.objects.get(id=pixel_id)
    except Pixel.DoesNotExist:
        raise Http404("Pixel does not exist")
    # verify that the tracker exists
    try:
        trackerObject = Tracker.objects.get(id=tracker_id)
    except Tracker.DoesNotExist:
        raise Http404("Tracker does not exist")
    # verify that the tracker belongs to the pixel
    if trackerObject not in pixelObject.tracker_set.all():
        raise Http404("The tracker is not from the given pixel")
    # check that the user owns the pixel, then display the header in plaintext
    if pixelObject.owner != request.user:
        raise PermissionDenied("You are not the owner of the pixel associated to this tracker")
    else:
        return HttpResponse(f"<samp>{trackerObject.header}</samp>")
