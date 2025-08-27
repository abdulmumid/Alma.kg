from django.contrib import admin
from django.utils.safestring import mark_safe
from leaflet.admin import LeafletGeoAdmin
from .models import HurryBuy, Board, Stock, Story, Store

class ImagePreviewMixin:
    @admin.display(description='Изображение')
    def image_preview(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:100px; max-width:100px;" />')
        return 'Нет изображения'


# 📌 Доски
@admin.register(Board)
class BoardAdmin(ImagePreviewMixin, admin.ModelAdmin):
    icon_name = "dashboard"
    list_display = ('title', 'slug', 'image_preview', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')


# 📌 Акции
@admin.register(Stock)
class StockAdmin(ImagePreviewMixin, admin.ModelAdmin):
    icon_name = "local_offer"
    list_display = ('title', 'image_preview', 'created_at', 'updated_at')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
    fields = ('title', 'description', 'image', 'image_preview', 'created_at', 'updated_at')


# 📌 Сторисы
@admin.register(Story)
class StoryAdmin(ImagePreviewMixin, admin.ModelAdmin):
    icon_name = "history"
    list_display = ('title', 'image_preview', 'is_active', 'created_at', 'updated_at')
    search_fields = ('title',)
    list_filter = ('is_active',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')


# 📌 Магазины
@admin.register(Store)
class StoreAdmin(LeafletGeoAdmin):
    icon_name = "store"
    list_display = ("name", "address", "is_open_24h", "working_hours")
    search_fields = ("name", "address")
    list_filter = ("is_open_24h",)


# 📌 Срочная покупка
@admin.register(HurryBuy)
class HurryBuyAdmin(ImagePreviewMixin, admin.ModelAdmin):
    icon_name = "flash_on"
    list_display = ('title', 'price', 'percent_discount', 'start_date', 'end_date', 'created_at', 'updated_at', 'image_preview')
    search_fields = ('title',)
    readonly_fields = ('image_preview', 'created_at', 'updated_at')
