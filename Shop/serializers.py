from rest_framework import serializers
from .models import Cart, CartItem, Order, DeliveryRegion


# 🔹 Сериализатор элемента корзины
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_name", "quantity", "final_price"]

    def get_final_price(self, obj):
        return obj.get_total_price()


# 🔹 Сериализатор корзины
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "items", "total_price", "is_active"]

    def get_total_price(self, obj):
        return obj.get_total_price()


# 🔹 Сериализатор заказа
class OrderSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.none())
    items = CartItemSerializer(source="cart.items", many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Только активные корзины пользователя
            self.fields['cart'].queryset = Cart.objects.filter(user=request.user, is_active=True)

    def get_total_price(self, obj):
        return obj.total_price

    def create(self, validated_data):
        order = super().create(validated_data)
        order.apply_bonuses()
        order.award_bonuses()
        return order


# 🔹 Сериализатор регионов доставки
class DeliveryRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryRegion
        fields = ["id", "name"]
