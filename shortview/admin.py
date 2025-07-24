from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Profile, Link, Tracker

# Change admin page headers
admin.site.site_header = _("ShortView Administration")
admin.site.site_title = _("ShortView Admin Portal")
admin.site.index_title = _("Welcome to the ShortView Administration Interface")

# Register your models here.
class ProfileInLine(admin.TabularInline):
    model = Profile
    can_delete = False


class LinkInLine(admin.TabularInline):
    model = Link
    extra = 0
    classes=["collapse"]


class UserAdminCustom(UserAdmin):
    """
    keep the default admin entries, but add inlines
    """
    inlines = [ProfileInLine, LinkInLine]
    list_display = ["username", "email", "is_staff"]


class TrackerInLine(admin.TabularInline):
    model = Tracker
    extra = 0
    classes=["collapse"]


class LinkAdmin(admin.ModelAdmin):
    """
    section to manage links and their trackers
    """
    fieldsets = [
        (_("General"), {"fields": ["owner", "description", "destination"]}),
        (_("Date and time"), {"fields": ["date", "lifetime"]}),
        (_("Email notifications"), {"fields": ["notify_click"]}),
    ]
    inlines = [TrackerInLine]
    list_display = ["description", "owner", "short_destination", "date", "active"]
    list_filter = ["date", "owner"]
    search_fields = ["description"]


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
admin.site.register(Link, LinkAdmin)
