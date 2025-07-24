from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings

from urllib.parse import urlparse
import datetime

# Create your models here.

class Profile(models.Model):
    """
    a model to store a user profile, with all its settings, data and preferences
    """
    NOTIFY_CLICK_CHOICES = [(1, _("Never notify")), (2, _("Notify first click")), (3, _("Notify each click"))]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    delete_expired = models.BooleanField(_("delete expired links"), default=False)
    hide_expired = models.BooleanField(_("hide expired links"), default=True)
    default_lifetime = models.DurationField(_("default link life duration"), default=datetime.timedelta(0))
    default_notify_click = models.IntegerField(_("send email on link click"), choices=NOTIFY_CLICK_CHOICES, default=1)
    receive_newsletters = models.BooleanField(_("receive the newsletters"), default=True)

    def __str__(self):
        return str(_("%(user)s's profile") % {"user": self.user})


class Link(models.Model):
    """
    a model to represent a tracked link shortener with its attributes
    """
    NOTIFY_CLICK_CHOICES = [(0, _("User preference")), (1, _("Never notify")), (2, _("Notify first click")), (3, _("Notify each click"))]

    description = models.CharField(_("description"), default="", max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # user who owns the link
    date = models.DateTimeField(_("date of creation"))
    lifetime = models.DurationField(_("life duration"), default=datetime.timedelta(0))  # 0 for unlimited
    notify_click = models.IntegerField(_("send email on link click"), choices=NOTIFY_CLICK_CHOICES, default=0)
    destination = models.URLField(_("destination url"), default="https://example.com/", max_length=65535)
    
    def url(self):
        """
        returns the absolute url to the shortened link
        """
        path = reverse("redirect_link", args=[self.id])
        domain = Site.objects.get_current().domain
        scheme = "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http"
        return f"{scheme}://{domain}{path}"
    
    @admin.display(
        ordering="destination",
        description=_("destination domain"),
    )
    def short_destination(self):
        """
        returns only the domain of the destination url
        """
        return urlparse(self.destination).netloc
    
    @admin.display(
        boolean=True,
        ordering="date",
        description=_("still active"),
    )
    def active(self) -> bool:
        """
        is the link still active, False if expired
        """
        if self.lifetime == datetime.timedelta(0):
            return True
        # return True if the link isn't expired and is not scheduled to be active in the future
        return self.lifetime >= timezone.now() - self.date and self.date <= timezone.now()
    
    def __str__(self):
        return f"{self.description} --> {self.short_destination()}"


class Tracker(models.Model):
    """
    a model to store the informations when a link has been clicked, a link can have multiple trackers
    """
    link = models.ForeignKey(Link, on_delete=models.CASCADE)  # the link from which the tracking originates
    ip = models.GenericIPAddressField(_("receiver ip"), default="0.0.0.0")
    date = models.DateTimeField(_("date of clicking"))
    header = models.TextField(_("request header"), default="")

    def __str__(self):
        return f"{self.ip} | {self.date}"
