from django.shortcuts import redirect, render, get_object_or_404
from django.conf import settings
from django.http import HttpRequest, HttpResponse, Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.urls import resolve, reverse, Resolver404
from django.utils import timezone
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from .models import Profile, Link, Tracker
from . import jobs, tools

from urllib.parse import urlparse
from threading import Thread
import datetime
import json
import re

# Create your views here.

@tools.regular_jobs
def index(request: HttpRequest):
    """
    the view to display the index page, or the home page if the user is logged in
    """
    if not request.user.is_authenticated:
        return render(request, "shortview/index.html")

    # sort links
    links = request.user.link_set.all().order_by("-date")
    active, expired = [], []
    for link in links:
        if not link.date > timezone.now():
            if link.active():
                active.append(link)
            else:
                expired.append(link)
    
    sorted_links = active + expired
    return render(request, "shortview/home.html", {"user": request.user,
                                                   "profile": request.user.profile,
                                                   "links": sorted_links,
                                                   })


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
        return render(request, "shortview/register.html")
    
    # if POST data has been received to try a registration
    # check username validity
    if not re.fullmatch(r"^[A-Za-z0-9_.+-]{3,50}$", username):
        return render(request, "shortview/register.html", {"error": "The username format is invalid, it must be between 3 and 50 characters, can only contain letters, numbers, and these symbols:  _ + . -",
                                                          "username": username,
                                                          "email": email,
                                                          })
    if User.objects.filter(username=username).exists():
        return render(request, "shortview/register.html", {"error": "This username already exists, try another one, or use the log in page if your account already exists.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    
    # check email validity
    if not re.fullmatch(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$", email):
        return render(request, "shortview/register.html", {"error": "The email format is invalid, please enter a valid email address.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    if User.objects.filter(email=email).exists():
        return render(request, "shortview/register.html", {"error": "This email address is already in use, try logging in with it.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    
    # check basic password validity
    if password != password_confirm:
        return render(request, "shortview/register.html", {"error": "The two passwords you entered are different, you need to enter the same password twice.",
                                                          "username": username,
                                                          "email": email,
                                                          })
    
    # try registering with the given credentials
    try:
        validate_password(password)
    except ValidationError as e:
        # if the password is not valid, return the error message(s)
        return render(request, "shortview/register.html", {"error": f"The password you entered is not valid. {' '.join(e.messages)}",
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
        return render(request, "shortview/login.html")
    
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
        return render(request, "shortview/login.html", {"error": f"The {login_type} you entered is invalid. Make sure the {login_type} is correct, or use the sign in button to create a new account.",
                                                        "identifier": identifier,
                                                        })
    except User.MultipleObjectsReturned:
        # if there (somehow) are multiple users possible
        return render(request, "shortview/login.html", {"error": f"Multiple different users are using this {login_type}. This is an issue, please contact the developper to fix this.",
                                                        "identifier": identifier,
                                                        })
    
    # log the user in if everything is ok
    username = user_object.username
    user = authenticate(request, username=username, password=password)
    if user is None:
        return render(request, "shortview/login.html", {"error": "The credentials are invalid, make sure that the password is correct.",
                                                        "identifier": identifier,
                                                        })
    else:
        login(request, user)
        if "next" in request.POST:
            return redirect(request.POST["next"])
        else:
            return redirect("index")


def logoutpage(request: HttpRequest):
    """
    logs out the current user
    """
    logout(request)
    return redirect("index")


def password_info(request: HttpRequest):
    """
    an informative page to explain to the user how passwords are stored
    """
    return render(request, "shortview/info/passwords.html")


def conditions(request: HttpRequest):
    """
    an informative page to explain the conditions of use of the service
    """
    return render(request, "shortview/info/conditions.html")


@login_required
@tools.regular_jobs
def preferences(request: HttpRequest):
    """
    the view to let the user change the preferences and set the new preferences using the POST data
    """    
    profile:Profile = request.user.profile

    default_lifetime:datetime.timedelta = profile.default_lifetime
    default_hours = default_lifetime.seconds // 3600
    default_minutes = (default_lifetime.seconds % 3600) // 60
    default_seconds = default_lifetime.seconds % 60
    
    required_post_data = ["notify"]
    never_expire = request.POST["never_expire"] == "on" if "never_expire" in request.POST else False
    newsletter = request.POST["newsletter"] == "on" if "newsletter" in request.POST else False
    if never_expire and all(element in request.POST for element in required_post_data):
        days, hours, minutes, seconds = 0, 0, 0, 0
        notify = request.POST["notify"]
    elif all(element in request.POST for element in ["days", "hours", "minutes", "seconds"] + required_post_data):
        days = request.POST["days"]
        hours = request.POST["hours"]
        minutes = request.POST["minutes"]
        seconds = request.POST["seconds"]
        notify = request.POST["notify"]
    else:  # missing post data, user want the page
        return render(request, "shortview/preferences.html", {"profile": profile,
                                                              "notify": profile.default_notify_click,
                                                              "newsletter": profile.receive_newsletters,
                                                              "delete_expired": profile.delete_expired,
                                                              "never_expire": profile.default_lifetime == datetime.timedelta(0),
                                                              "days": default_lifetime.days, "hours": default_hours, "minutes": default_minutes, "seconds": default_seconds,
                                                              })
    
    # continue handling post data
    try:
        days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
    except ValueError:
        return render(request, "shortview/preferences.html", {"profile": profile,
                                                              "notify": profile.default_notify_click,
                                                              "newsletter": newsletter,
                                                              "delete_expired": profile.delete_expired,
                                                              "never_expire": profile.default_lifetime == datetime.timedelta(0),
                                                              "days": default_lifetime.days, "hours": default_hours, "minutes": default_minutes, "seconds": default_seconds,
                                                              "error": "Error: You tried to set the lifetime value without using integers.",
                                                              })
    try:
        notify = int(notify)
    except ValueError:
        return render(request, "shortview/preferences.html", {"profile": profile,
                                                              "notify": profile.default_notify_click,
                                                              "newsletter": newsletter,
                                                              "delete_expired": profile.delete_expired,
                                                              "never_expire": profile.default_lifetime == datetime.timedelta(0),
                                                              "days": days, "hours": hours, "minutes": minutes, "seconds": seconds,
                                                              "error": "Error: The value for the notification preference is invalid",
                                                              })
    else:
        if not 1 <= notify <= 3:
            return render(request, "shortview/preferences.html", {"profile": profile,
                                                                "notify": profile.default_notify_click,
                                                                "newsletter": newsletter,
                                                                "delete_expired": profile.delete_expired,
                                                                "never_expire": profile.default_lifetime == datetime.timedelta(0),
                                                                "days": days, "hours": hours, "minutes": minutes, "seconds": seconds,
                                                                "error": "Error: The value for the notification preference is invalid",
                                                                })
    
    delete_expired = request.POST["delete_expired"] == "on" if "delete_expired" in request.POST else False
    hide_expired = request.POST["hide_expired"] == "on" if "hide_expired" in request.POST else False
    
    # modify the profile
    profile:Profile = request.user.profile
    profile.default_notify_click = notify
    profile.receive_newsletters = newsletter
    profile.default_lifetime = datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    profile.delete_expired = delete_expired
    profile.hide_expired = hide_expired
    profile.save()
    return render(request, "shortview/preferences.html", {"profile": profile,
                                                          "notify": notify,
                                                          "newsletter": newsletter,
                                                          "delete_expired": delete_expired,
                                                          "never_expire": never_expire,
                                                          "days": days, "hours": hours, "minutes": minutes, "seconds": seconds,
                                                          "success": "Successfully applied the new preferences!",
                                                          })


@login_required
@tools.regular_jobs
def new_link(request: HttpRequest):
    """
    allow the user to create a new tracked link
    """    
    profile:Profile = request.user.profile

    default_lifetime:datetime.timedelta = profile.default_lifetime
    default_hours = default_lifetime.seconds // 3600
    default_minutes = (default_lifetime.seconds % 3600) // 60
    default_seconds = default_lifetime.seconds % 60

    # if we have the post data, then we create the link, else we send the page
    never_expire = request.POST["never_expire"] == "on" if "never_expire" in request.POST else False
    required_post_data = ["description", "destination", "notify"]
    if never_expire and all(element in request.POST for element in required_post_data):
        days, hours, minutes, seconds = 0, 0, 0, 0
        description = request.POST["description"]
        destination = request.POST["destination"]
        notify = request.POST["notify"]
    elif all(element in request.POST for element in ["days", "hours", "minutes", "seconds"] + required_post_data):
        days = request.POST["days"]
        hours = request.POST["hours"]
        minutes = request.POST["minutes"]
        seconds = request.POST["seconds"]
        description = request.POST["description"]
        destination = request.POST["destination"]
        notify = request.POST["notify"]
    
    else:  # missing post data, user want the page
        return render(request, "shortview/new_link.html", {"never_expire": profile.default_lifetime == datetime.timedelta(0),
                                                           "notify": 0,
                                                           "days": default_lifetime.days, "hours": default_hours, "minutes": default_minutes, "seconds": default_seconds,
                                                           })
    
    # continue handling post data
    try:
        days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
    except ValueError:
        return render(request, "shortview/new_link.html", {"description": description,
                                                           "destination": destination,
                                                           "notify": 0,
                                                           "never_expire": never_expire,
                                                           "days": default_lifetime.days, "hours": default_hours, "minutes": default_minutes, "seconds": default_seconds,
                                                           "error": "Error: You tried to set the lifetime value without using integers.",
                                                           })
    try:
        notify = int(notify)
    except ValueError:
        return render(request, "shortview/new_link.html", {"description": description,
                                                           "destination": destination,
                                                           "notify": 0,
                                                           "never_expire": never_expire,
                                                           "days": days, "hours": hours, "minutes": minutes, "seconds": seconds,
                                                           "error": "Error: You tried to set the lifetime value without using integers.",
                                                           })
    else:
        if not 0 <= notify <= 3:
            return render(request, "shortview/new_link.html", {"description": description,
                                                               "destination": destination,
                                                               "notify": 0,
                                                               "never_expire": never_expire,
                                                               "days": days, "hours": hours, "minutes": minutes, "seconds": seconds,
                                                               "error": "Error: You tried to set the lifetime value without using integers.",
                                                               })

    # check that the destination is not another redirection to avoid loops
    destination_path = urlparse(destination).path
    try:
        pattern = resolve(destination_path)
    except Resolver404:
        pass
    else:
        if pattern.url_name == "redirect_link":
            return render(request, "shortview/new_link.html", {"description": description,
                                                               "destination": destination,
                                                               "notify": profile.default_notify_click,
                                                               "never_expire": never_expire,
                                                               "days": days, "hours": hours, "minutes": minutes, "seconds": seconds,
                                                               "error": "Error: You cannot set another tracked url as the destination.",
                                                               })
    
    # create the new link
    link:Link = Link(owner=request.user, description=description, date=timezone.now(), destination=destination, notify_click=notify,
                      lifetime=datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds),
                      )
    link.save()
    return redirect("view_link", link.id)


@login_required
@tools.regular_jobs
def view_link(request: HttpRequest, link_id: int):
    """
    displays info about a tracked link, if it belongs to the active user
    """
    # verify that the link exists
    try:
        link_object = Link.objects.get(id=link_id)
    except Link.DoesNotExist:
        raise Http404("Link does not exist")
    else:
        # check that the user owns the link, then display the page
        if link_object.owner == request.user:
            return render(request, "shortview/view_link.html", {"link": link_object,
                                                                "trackers": link_object.tracker_set.all(),
                                                                })
        else:
            raise PermissionDenied("You are not the owner of this link")


@login_required
@tools.regular_jobs
def delete_link(request: HttpRequest, link_id: int):
    """
    delete the link if the correct post data is given and the user owns it
    """
    try:
        link_object:Link = Link.objects.get(id=link_id)
    except Link.DoesNotExist:
        return redirect("view_link", link_id)

    if not "confirm_delete" in request.POST:
        return redirect("view_link", link_id)
    
    if not (request.user.is_authenticated and request.user == link_object.owner):
        return redirect("view_link", link_id)
    
    # delete the link object
    link_object.delete()
    return redirect("index")


@login_required
@tools.regular_jobs
def link_change_notify(request: HttpRequest, link_id: int):
    """
    change the notification preference for a specific link
    """
    try:
        link_object:Link = Link.objects.get(id=link_id)
    except Link.DoesNotExist:
        return redirect("view_link", link_id)

    if not "notify" in request.POST:
        return redirect("view_link", link_id)
    
    if not (request.user.is_authenticated and request.user == link_object.owner):
        return redirect("view_link", link_id)
    
    notify = request.POST["notify"]
    try:
        notify = int(notify)
    except ValueError:
        return redirect("view_link", link_id)
    if not (0 <= notify <= 3):
        return redirect("view_link", link_id)
    
    link_object.notify_click = notify
    link_object.save()
    return redirect("view_link", link_id)


def redirect_link(request: HttpRequest, link_id: int):
    """
    log the request by creating a tracker and serve the destination page to the client
    """
    # check that the link exists
    try:
        link_object:Link = Link.objects.get(id=link_id)
    except Link.DoesNotExist:
        raise Http404("link does not exist")
    # check that the link is active
    if not link_object.active():
        raise Http404("link expired")
    # do not log if the link is clicked by the owner
    if request.user.is_authenticated and request.user == link_object.owner:
        return redirect(link_object.destination)

    # get the ip address (ipv6 or ipv4)
    ip = request.META.get("HTTP_X_FORWARDED_FOR")
    if ip:
        ip = ip.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    
    # get the header as json and remove sensitive data
    header = dict(request.headers)
    header["Cookie"] = "[REDACTED]"
    header_json = json.dumps(header, indent=2)

    # do not log if the link has been opened by an app agent to generate a preview
    agents_blacklist = ["whatsapp", "discord", "slack"]
    if any([agent.lower() in header["User-Agent"].lower() for agent in agents_blacklist]):
        return redirect(link_object.destination)

    # log the click
    tracker:Tracker = Tracker(link=link_object, date=timezone.now(), ip=ip, header=header_json)
    tracker.save()

    # notify by email depending on preferences
    if link_object.notify_click == 0:  # using default preference
        notify = link_object.owner.profile.default_notify_click
    else:
        notify = link_object.notify_click
    
    if (notify == 2 and link_object.tracker_set.count() == 1) or notify == 3:  # if notify first click and it is, or always notify
        # send an email notification
        domain = Site.objects.get_current().domain
        scheme = "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http"
        base_url = f"{scheme}://{domain}"
        link_page = f"{base_url}{reverse('view_link', args=[link_object.id])}"
        tracker_page = f"{base_url}{reverse('view_tracker', args=[link_object.id, tracker.id])}"
        preferences_page = f"{base_url}{reverse('preferences')}"

        text_content = render_to_string("shortview/emails/notify_click.txt",
                                        context={"link": link_object, "tracker": tracker, "link_page": link_page,
                                                 "tracker_page": tracker_page, "preferences_page": preferences_page,
                                                 "mail_domain": settings.DOMAIN, "username": link_object.owner.username})
        html_content = render_to_string("shortview/emails/notify_click.html",
                                        context={"link": link_object, "tracker": tracker, "link_page": link_page,
                                                 "tracker_page": tracker_page, "preferences_page": preferences_page,
                                                 "mail_domain": settings.DOMAIN, "username": link_object.owner.username})
        email_thread = Thread(target=tools.send_email,args=[f"ShortView | Your link was clicked | {link_object.description}",
                                                           settings.DEFAULT_FROM_EMAIL, link_object.owner.email, text_content, html_content])
        email_thread.daemon = True
        email_thread.start()
    
    return redirect(link_object.destination)


@login_required
@tools.regular_jobs
def view_tracker(request: HttpRequest, link_id:int, tracker_id:int):
    """
    view the full header of a request to the tracked link, also verifies if the page url is consistent
    the used page url contains the link id for the sake of easy navigation for the user
    """
    # verify that the link exists
    try:
        link_object = Link.objects.get(id=link_id)
    except Link.DoesNotExist:
        raise Http404("Link does not exist")
    # verify that the tracker exists
    try:
        tracker_object = Tracker.objects.get(id=tracker_id)
    except Tracker.DoesNotExist:
        raise Http404("Tracker does not exist")
    # verify that the tracker belongs to the link
    if tracker_object not in link_object.tracker_set.all():
        raise Http404("The tracker is not from the given link")
    # check that the user owns the link, then display the header in plaintext
    if link_object.owner != request.user:
        raise PermissionDenied("You are not the owner of the link associated to this tracker")
    else:
        return HttpResponse(tracker_object.header, content_type="application/json")
