from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Notification

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_verified')
    list_filter = ('is_staff', 'is_verified', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)  # <-- заменили username на email
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'birth_date', 'qr_code')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_verified')}
        ),
    )

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
