from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Verification

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "phone", "first_name", "last_name", "is_active", "is_staff", "qr_thumb")
    ordering = ("email",)
    search_fields = ("email", "phone", "first_name", "last_name")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личные данные", {"fields": ("first_name", "last_name", "phone")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Даты", {"fields": ("last_login", "date_joined")}),
        ("QR", {"fields": ("qr_payload", "qr_code")}),
    )
    readonly_fields = ("qr_payload", "qr_code")

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "phone", "first_name", "last_name", "password1", "password2", "is_active", "is_staff", "is_superuser"),
        }),
    )

    def qr_thumb(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="64" height="64" />')
        return "-"
    qr_thumb.short_description = "QR"


@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose", "code", "is_used", "created_at")
    search_fields = ("user__email", "code")
    list_filter = ("purpose", "is_used", "created_at")
