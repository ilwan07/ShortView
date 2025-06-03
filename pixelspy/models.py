from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

# Create your models here.
class Pixel(models.Model):
    """
    a model to represent a tracking pixel with its attributes
    """
    description = models.CharField("pixel user description", default="")
    date = models.DateTimeField("date of creation")
    lifetime = models.DurationField("life duration", default=datetime.timedelta(0))  # 0 for unlimited
    url = models.URLField("pixel display url")
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # user who owns the pixel

    def __str__(self):
        if self.url is not None:
            return str(self.url).split("/")[-1]
        else:
            return super().__str__()
    
    def is_expired(self) -> bool:
        return self.lifetime >= timezone.now() - self.date


class Tracker(models.Model):
    """
    a model to store the informations when a mail has been read once, a pixel can have multiple trackers
    """
    pixel = models.ForeignKey(Pixel, on_delete=models.CASCADE)  # the pixel from which the tracking originates
    date = models.DateField("date of opening")
    ip = models.GenericIPAddressField("receiver ip")
    header = models.CharField("request header metadata", default="")

    def __str__(self):
        return f"{str(self.date)} from {self.ip}"
