from rest_framework import serializers
from .models import DeliveryRegion, DeliveryAddress, Order, CartItem
from Product.models import Product


class DeliveryRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRegion
        fields = "__all__"


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = "__all__"
        read_only_fields = ["user"]


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ["product", "quantity"]


class OrderSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["id", "region", "total_price", "status", "created_at", "items"]
        read_only_fields = ["user", "status", "total_price", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user
        order = Order.objects.create(user=user, **validated_data)

        total = 0
        for item_data in items_data:
            cart_item = CartItem.objects.create(order=order, **item_data)
            total += cart_item.get_total_price()

        order.total_price = total
        order.save()
        return order
