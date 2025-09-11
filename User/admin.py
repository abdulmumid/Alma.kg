from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import CustomUser, OTP, UserBonus, BonusTransaction, Notification, DeliveryAddress

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    icon_name = "person"
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_verified', 'is_active')
    list_filter = ('is_staff', 'is_verified', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Права', {'fields': ('is_staff', 'is_active', 'is_verified', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важное', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_verified')}
        ),
    )

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    icon_name = "vpn_key"
    list_display = ('user', 'code', 'purpose', 'is_used', 'created_at', 'expires_at_display')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('user__email', 'code')
    readonly_fields = ('created_at',)

    @admin.display(description="Истекает")
    def expires_at_display(self, obj):
        return obj.expires_at

@admin.register(UserBonus)
class UserBonusAdmin(admin.ModelAdmin):
    icon_name = "star"
    list_display = ('user', 'total_points', 'available_points')
    search_fields = ('user__email', 'user__phone_number')
    readonly_fields = ('total_points', 'available_points')

@admin.register(BonusTransaction)
class BonusTransactionAdmin(admin.ModelAdmin):
    icon_name = "monetization_on"
    list_display = ('user', 'points', 'transaction_type', 'description', 'qr_code', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__email', 'description', 'qr_code')
    readonly_fields = ('user', 'points', 'transaction_type', 'description', 'qr_code', 'created_at')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    icon_name = "notifications"
    list_display = ('user', 'short_message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'message')
    readonly_fields = ('created_at',)
    actions = ['send_to_all_users']

    @admin.display(description="Сообщение")
    def short_message(self, obj):
        return str(obj.message)[:50] + ("..." if len(str(obj.message)) > 50 else "")

    @admin.action(description="Отправить уведомление всем пользователям")
    def send_to_all_users(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Нет выбранных уведомлений для отправки.", level=messages.WARNING)
            return
        users = CustomUser.objects.filter(is_active=True)
        notifications = [Notification(user=user, message=obj.message) for obj in queryset for user in users]
        Notification.objects.bulk_create(notifications, batch_size=500)
        self.message_user(
            request,
            f"Отправлено {len(notifications)} уведомлений ({users.count()} пользователям).",
            level=messages.SUCCESS
        )

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    icon_name = "place"
    list_display = ('user', 'full_address_display', 'region', 'is_default')
    list_filter = ('region', 'is_default')
    search_fields = ('user__email', 'street', 'house', 'region__name')
    ordering = ('user',)

    @admin.display(description="Адрес")
    def full_address_display(self, obj):
        return obj.full_address()
