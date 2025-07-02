from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings

import datetime

# Create your models here.

class Profile(models.Model):
    """
    a model to store a user profile, with all its settings, data and preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hide_expired = models.BooleanField("hide expired pixels", default=True)
    default_lifetime = models.DurationField("default pixel life duration", default=datetime.timedelta(days=14))

    def __str__(self):
        return str(self.user)


class Pixel(models.Model):
    """
    a model to represent a tracking pixel with its attributes
    """
    description = models.CharField("description", default="")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # user who owns the pixel
    date = models.DateTimeField("date of creation")
    lifetime = models.DurationField("life duration", default=datetime.timedelta(0))  # 0 for unlimited

    def __str__(self):
        if self.description:
            return self.description
        else:
            return super().__str__()
    
    def url(self):
        """
        returns the absolute url to display the pixel
        """
        path = reverse("display_pixel", args=[self.id])
        domain = Site.objects.get_current().domain
        scheme = "https" if getattr(settings, "SECURE_SSL_REDIRECT", False) else "http"
        return f"{scheme}://{domain}{path}"
    
    @admin.display(
        boolean=True,
        ordering="date",
        description="still active",
    )
    def active(self) -> bool:
        """
        is the pixel still active, False if expired
        """
        if self.lifetime == datetime.timedelta(0):
            return True
        # return True if the pixel isn't expired and is not scheduled to be active in the future
        return self.lifetime >= timezone.now() - self.date and self.date <= timezone.now()


class Tracker(models.Model):
    """
    a model to store the informations when a mail has been read once, a pixel can have multiple trackers
    """
    pixel = models.ForeignKey(Pixel, on_delete=models.CASCADE)  # the pixel from which the tracking originates
    ip = models.GenericIPAddressField("receiver ip")
    date = models.DateTimeField("date of opening")
    header = models.CharField("request header", default="")

    def __str__(self):
        return f"{self.ip} | {self.date}"
