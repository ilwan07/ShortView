from django.core.mail import EmailMultiAlternatives

# Below are other functions which can be used elsewhere

def send_email(subject:str, sender:str, receiver:str, text_content:str, html_content:str=None):
    email = EmailMultiAlternatives(subject, text_content, sender, [receiver])
    if html_content is not None:
        email.attach_alternative(html_content, "text/html")
    email.send()
