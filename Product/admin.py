from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category_Product, Product, Cart, CartItem, Address, Order, OrderItem


# 🔹 Миксин для превью изображений
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
        'barcode', 'image_preview', 'is_featured', 'store'
    )
    search_fields = ('name', 'barcode')
    list_filter = ('is_featured', 'category', 'store')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fields = (
        'name', 'category', 'price', 'discount', 'barcode', 'label',
        'image', 'image_preview', 'is_featured', 'store',
        'created_at', 'updated_at'
    )

    @admin.display(description="Цена со скидкой")
    def final_price_display(self, obj):
        return f"{obj.final_price:.2f}"


# 📌 Корзина
class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    icon_name = "shopping_cart"
    list_display = ('user', 'created_at')
    search_fields = ('user__phone', 'user__email')
    list_filter = ('created_at',)
    inlines = [CartItemInline]
    readonly_fields = ('created_at',)


# 📌 Элемент корзины
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    icon_name = "add_shopping_cart"
    list_display = ('cart', 'product', 'quantity', 'created_at', 'updated_at')
    search_fields = ('cart__user__phone', 'product__name')
    readonly_fields = ('created_at', 'updated_at')


# 📌 Адреса пользователей
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    icon_name = "location_on"
    list_display = ('user', 'street', 'house', 'created_at')
    search_fields = ('street', 'house', 'user__phone')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


# 📌 Заказы
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    icon_name = "receipt_long"
    list_display = ('id', 'user', 'address', 'total', 'created_at')
    search_fields = ('user__phone', 'user__email', 'id')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]


# 📌 Элементы заказа
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    icon_name = "inventory_2"
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__id', 'product__name')
