from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from leaflet.admin import LeafletGeoAdmin

from .models import (
    HurryBuy, Notification, Board, Stock, Story, Store
)

User = get_user_model()


# 🔹 Миксин для превью изображений
class ImagePreviewMixin:
    def image_preview(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:100px; max-width:100px;" />')
        return 'Нет изображения'
    image_preview.short_description = 'Изображение'


# 📌 Доски
@admin.register(Board)
class BoardAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'image_preview', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')


# 📌 Акции
@admin.register(Stock)
class StockAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'created_at', 'updated_at')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    fields = ('title', 'description', 'image', 'image_preview', 'created_at', 'updated_at')


# 📌 Сторисы
@admin.register(Story)
class StoryAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'image_preview', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('is_active',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')


# 📌 Магазины
@admin.register(Store)
class StoreAdmin(LeafletGeoAdmin):
    list_display = ("name", "address", "is_open_24h", "working_hours")
    search_fields = ("name", "address")
    list_filter = ("is_open_24h",)


# 📌 Срочная покупка
@admin.register(HurryBuy)
class HurryBuyAdmin(ImagePreviewMixin, admin.ModelAdmin):
    list_display = ('title', 'price', 'percent_discount', 'start_date', 'end_date', 'created_at', 'updated_at', 'image_preview')
    search_fields = ('title',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')


# 📌 Уведомления
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__phone', 'user__email', 'message')
    list_filter = ('is_read', 'created_at')
    readonly_fields = ('created_at',)
    actions = ['send_to_all_users']

    @admin.action(description="Отправить уведомление всем пользователям")
    def send_to_all_users(self, request, queryset):
        users = list(User.objects.only('id'))  # только id для скорости
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
