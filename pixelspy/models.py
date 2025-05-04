from django.db import models
import datetime

# Create your models here.
class Pixel(models.Model):
    """
    a model to represent a tracking pixel with its attributes
    """
    creation_date = models.DateTimeField("date of creation")  # date of creation of the image object
    life_duration = models.DurationField("life duration", default=datetime.timedelta(0))  # time for which the image will exist (0 for unlimited)
    user_owner = models.CharField("pixel owner")  # username of the owner of this image

class Tracker(models.Model):
    """
    a model to store the informations when a mail has been read
    """
    pixel = models.ForeignKey(Pixel, on_delete=models.CASCADE)  # the pixel from which the tracking originates
    opened_date = models.DateField("date of opening")  # date for which the mail was opened
    ip = models.GenericIPAddressField("receiver ip")  # ip address of the mail receiver
