from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

from .models import Profile, Pixel, Tracker

# Change admin page headers
admin.site.site_header = "PixelSpy Administration"
admin.site.site_title = "PixelSpy Admin Portal"
admin.site.index_title = "Welcome to the PixelSpy Administration Interface"

# Register your models here.
class PixelInLine(admin.TabularInline):
    model = Pixel
    extra = 0


class ProfileInLine(admin.TabularInline):
    model = Profile
    can_delete = False


class UserAdminCustom(UserAdmin):
    """
    keep the default admin entries, but add inlines
    """
    inlines = [ProfileInLine, PixelInLine]


class TrackerInLine(admin.TabularInline):
    model = Tracker
    extra = 0


class PixelAdmin(admin.ModelAdmin):
    """
    section to manage pixels and their trackers
    """
    fieldsets = [
        ("General", {"fields": ["description", "owner"]}),
        ("Date and time", {"fields": ["date", "lifetime"]}),
        ("Information", {"fields": ["url"]}),
    ]
    inlines = [TrackerInLine]
    list_display = ["description", "owner", "date", "active"]
    list_filter = ["date", "owner"]
    search_fields = ["description"]


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
admin.site.register(Pixel, PixelAdmin)
