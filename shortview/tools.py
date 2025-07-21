
from django.http import HttpRequest
from django.core.mail import EmailMultiAlternatives

from . import jobs

# Below are other functions which can be used elsewhere

def send_email(subject:str, sender:str, receiver:str, text_content:str, html_content:str=None):
    email = EmailMultiAlternatives(subject, text_content, sender, [receiver])
    if html_content is not None:
        email.attach_alternative(html_content, "text/html")
    email.send()

def regular_jobs(func):
    """
    do some regular jobs for authenticated users
    """
    def wrapper(*args, **kwargs):
        request: HttpRequest = args[0]
        if request.user.is_authenticated:
            # Ensure the user has a profile and delete expired links
            jobs.check_profiles(request.user)
            jobs.delete_expired_links(request.user)
        return func(*args, **kwargs)
    
    return wrapper
