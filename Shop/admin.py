from django.contrib import admin
from .models import DeliveryRegion, DeliveryAddress, Order, CartItem


@admin.register(DeliveryRegion)
class DeliveryRegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "region", "street", "house", "is_default")
    list_filter = ("region", "is_default")
    search_fields = ("street", "house")


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "region", "total_price", "status", "created_at")
    list_filter = ("status", "region", "created_at")
    inlines = [CartItemInline]
