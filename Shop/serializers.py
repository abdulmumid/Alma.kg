from rest_framework import serializers
from .models import Cart, CartItem, Order, DeliveryRegion

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "final_price"]

    def get_final_price(self, obj):
        return obj.get_total_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price", "is_active"]

    def get_total_price(self, obj):
        return obj.total_price


class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source="cart.items", many=True, read_only=True)
    spent_bonus = serializers.SerializerMethodField()
    earned_bonus = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    address_display = serializers.CharField(source="address.full_address", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "user", "cart", "items", "address", "address_display",
            "total_price", "used_bonus_points", "spent_bonus", "earned_bonus",
            "status", "created_at"
        ]
        read_only_fields = ["total_price", "status", "created_at", "spent_bonus", "earned_bonus"]

    def get_total_price(self, obj):
        return obj.total_price

    def get_spent_bonus(self, obj):
        return obj.used_bonus_points

    def get_earned_bonus(self, obj):
        bonus = 0
        for item in obj.cart.items.all():
            bonus += item.product.bonus_points * item.quantity
        return bonus


class DeliveryRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRegion
        fields = ["id", "name"]
