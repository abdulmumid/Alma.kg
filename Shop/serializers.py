from rest_framework import serializers
from .models import Cart, CartItem, Order, DeliveryRegion


class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    final_price = serializers.DecimalField(source="get_total_price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "final_price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(source="get_total_price", max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price", "is_active"]


class OrderSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.filter(is_active=True))
    items = CartItemSerializer(source="cart.items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "cart",
            "items",
            "address",
            "total_price",
            "used_bonus_points",
            "status",
            "created_at"
        ]
        read_only_fields = ["total_price", "status", "created_at"]

    def create(self, validated_data):
        order = super().create(validated_data)
        order.calculate_total_price()  # пересчёт суммы заказа
        order.apply_bonuses()          # списание бонусов
        order.award_bonuses()          # начисление бонусов
        return order


class DeliveryRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRegion
        fields = ["id", "name"]
