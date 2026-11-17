from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Address, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "username", "email_verified", "is_staff", "is_admin_user"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Storefront", {"fields": ("phone_number", "email_verified", "is_admin_user")}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "city", "state", "is_default"]
    list_filter = ["state", "is_default"]
    search_fields = ["full_name", "user__email"]
