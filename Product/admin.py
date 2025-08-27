from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category_Product, Product


class ImagePreviewMixin:
    @admin.display(description="Превью")
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" style="object-fit:contain;" />')
        return "-"


# 📌 Категории продуктов
@admin.register(Category_Product)
class CategoryProductAdmin(admin.ModelAdmin):
    icon_name = "category"
    list_display = ('name', 'slug', 'created_at', 'updated_at')
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')


# 📌 Продукты
@admin.register(Product)
class ProductAdmin(ImagePreviewMixin, admin.ModelAdmin):
    icon_name = "inventory_2"
    list_display = (
        'name', 'category', 'price', 'discount', 'final_price_display',
        'bonus_points', 'barcode', 'image_preview', 'is_featured', 'store'
    )
    search_fields = ('name', 'barcode')
    list_filter = ('is_featured', 'category', 'store')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fields = (
        'name', 'category', 'price', 'discount', 'bonus_points', 'barcode', 'label',
        'image', 'image_preview', 'is_featured', 'store',
        'created_at', 'updated_at'
    )

    @admin.display(description="Цена со скидкой")
    def final_price_display(self, obj):
        return f"{obj.final_price:.2f}"
