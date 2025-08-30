from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Notification, UserBonus, BonusTransaction, DeliveryAddress


# CustomUserAdmin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_verified')
    list_filter = ('is_staff', 'is_verified', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
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


# NotificationAdmin
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__phone_number', 'user__email', 'message')
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


# UserBonusAdmin
@admin.register(UserBonus)
class UserBonusAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points')
    search_fields = ('user__email', 'user__phone_number')
    readonly_fields = ('total_points',)


# BonusTransactionAdmin
@admin.register(BonusTransaction)
class BonusTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'transaction_type', 'description', 'qr_code', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__email', 'description', 'qr_code')
    readonly_fields = ('user', 'points', 'transaction_type', 'description', 'qr_code', 'created_at')


# DeliveryAddressAdmin
@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street', 'house', 'region', 'is_default')
    list_filter = ('region', 'is_default')
    search_fields = ('user__email', 'street', 'house')
    ordering = ('user',)
