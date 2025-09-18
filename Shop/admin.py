from django.contrib import admin
from .models import Cart, CartItem, Order, DeliveryRegion

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity", "get_total_price")

    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = "Итого"

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "created_at", "updated_at", "total_price_display")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__email",)
    inlines = [CartItemInline]

    def total_price_display(self, obj):
        return obj.total_price
    total_price_display.short_description = "Сумма корзины"

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity", "total_price_display")
    search_fields = ("product__name", "cart__user__email")

    def total_price_display(self, obj):
        return obj.get_total_price()
    total_price_display.short_description = "Итого"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "address_display", "total_price", "used_bonus_points", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "address__id")

    readonly_fields = ("cart_items_display",)

    def address_display(self, obj):
        return obj.address.full_address()
    address_display.short_description = "Адрес"

    def cart_items_display(self, obj):
        return "\n".join([f"{item.product.name} × {item.quantity}" for item in obj.cart.items.all()])
    cart_items_display.short_description = "Товары в корзине"

@admin.register(DeliveryRegion)
class DeliveryRegionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
