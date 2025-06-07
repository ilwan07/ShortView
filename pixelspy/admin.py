from django.contrib import admin
from .models import Pixel, Tracker
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class PixelInLine(admin.TabularInline):
    model = Pixel
    extra = 0


class UserAdminCustom(UserAdmin):
    """
    keep the default admin entries, but add an inline
    """
    inlines = [PixelInLine]


class TrackerInLine(admin.TabularInline):
    model = Tracker
    extra = 0


class PixelAdmin(admin.ModelAdmin):
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
