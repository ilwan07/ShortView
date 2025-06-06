from django.contrib import admin
from .models import Pixel, Tracker
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin

# Register your models here.

class PixelInLine(admin.TabularInline):
    model = Pixel
    extra = 0


class UserAdminCustom(UserAdmin):
    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name", "email"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("Important dates", {"fields": ["last_login", "date_joined"]}),
    ]
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


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdminCustom)
admin.site.register(Pixel, PixelAdmin)
