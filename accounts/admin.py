from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "promotion", "date_joined")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    list_editable = ("role",)
    search_fields = ("username", "email", "first_name", "last_name", "promotion")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Prépa IPEF", {"fields": ("role", "promotion", "bio")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Prépa IPEF", {"fields": ("email", "role", "promotion")}),
    )
