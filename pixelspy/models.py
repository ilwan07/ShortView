from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class Pixel(models.Model):
    """
    a model to represent a tracking pixel with its attributes
    """
    creation_date = models.DateTimeField("date of creation")  # date of creation of the image object
    life_duration = models.DurationField("life duration", default=datetime.timedelta(0))  # time for which the image will exist (0 for unlimited)
    display_url = models.URLField("pixel display url", default=None)  # url to use for requesting the image
    user_owner = models.CharField("pixel owner")  # username of the owner of this image  #TODO: point to user model directly

    def __str__(self):
        if self.display_url is not None:
            return self.display_url.split("/")[-1]
        else:
            return super().__str__()
    
    def is_expired(self) -> bool:
        return self.life_duration >= timezone.now() - self.creation_date


class Tracker(models.Model):
    """
    a model to store the informations when a mail has been read once, a pixel can have multiple trackers
    """
    pixel = models.ForeignKey(Pixel, on_delete=models.CASCADE)  # the pixel from which the tracking originates
    opened_date = models.DateField("date of opening")  # date for which the mail was opened
    ip = models.GenericIPAddressField("receiver ip")  # ip address of the mail receiver
    request_header = models.CharField("request header metadata", default="")  # full content of the request header

    def __str__(self):
        return f"{str(self.opened_date)} from {self.ip}"
