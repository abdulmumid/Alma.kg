from django.contrib import admin
from .models import Order, Cart, CartItem, DeliveryRegion


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("user__email",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")
    search_fields = ("product__name", "cart__user__email")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "address", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "address__street")


@admin.register(DeliveryRegion)
class DeliveryRegionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)