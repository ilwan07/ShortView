from django.shortcuts import render

# Create your views here.
def index(request):
    """
    the view to be displayed when requesting the pixelspy website
    """
    return render(request, "pixelspy/index.html")
