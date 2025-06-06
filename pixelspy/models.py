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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # user who owns the pixel
    date = models.DateTimeField("date of creation")
    lifetime = models.DurationField("life duration", default=datetime.timedelta(0))  # 0 for unlimited
    url = models.URLField("pixel display url")

    def __str__(self):
        if self.description:
            return self.description
        else:
            return super().__str__()
    
    def is_expired(self) -> bool:
        return self.lifetime >= timezone.now() - self.date


class Tracker(models.Model):
    """
    a model to store the informations when a mail has been read once, a pixel can have multiple trackers
    """
    pixel = models.ForeignKey(Pixel, on_delete=models.CASCADE)  # the pixel from which the tracking originates
    ip = models.GenericIPAddressField("receiver ip")
    date = models.DateTimeField("date of opening")
    header = models.CharField("request header metadata", default="")

    def __str__(self):
        return f"{self.date} from {self.ip}"
