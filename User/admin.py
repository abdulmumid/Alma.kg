from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Verification, Notification

# 📌 Пользователи
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    icon_name = "person" 
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

    @admin.display(description="QR")
    def qr_thumb(self, obj):
        if obj.qr_code:
            return mark_safe(f'<img src="{obj.qr_code.url}" width="64" height="64" />')
        return "-"


# 📌 Верификации
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    icon_name = "verified" 
    list_display = ("user", "purpose", "code", "is_used", "created_at")
    search_fields = ("user__email", "code")
    list_filter = ("purpose", "is_used", "created_at")


# 📌 Уведомления
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    icon_name = "notifications" 
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__phone', 'user__email', 'message')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('created_at',)
    actions = ['send_to_all_users']

    @admin.action(description="Отправить уведомление всем пользователям")
    def send_to_all_users(self, request, queryset):
        if not queryset:
            self.message_user(request, "Нет выбранных уведомлений для отправки.", level=messages.WARNING)
            return
        
        users = list(CustomUser.objects.only('id'))
        notifications = [
            Notification(user=user, message=obj.message)
            for obj in queryset
            for user in users
        ]
        Notification.objects.bulk_create(notifications, batch_size=500)
        
        self.message_user(
            request,
            f"Отправлено {len(notifications)} уведомлений ({len(users)} пользователям).",
            level=messages.SUCCESS
        )
