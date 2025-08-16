from rest_framework import serializers
from .models import *

# 📦 Категория продукта
class CategoryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category_Product
        fields = ['id', 'name', 'slug']

        
# 🛍️ Продукт
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# 🛒 Продукт (полный)
class ProductSerializer(serializers.ModelSerializer):
    category = CategoryProductSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


# 🍭 Продукт (упрощённый)
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image']


# 🛒 Элемент корзины
class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть не меньше 1.")
        return value


# 🛒 Корзина с вложенными элементами
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        cart = Cart.objects.create(**validated_data)
        CartItem.objects.bulk_create([
            CartItem(cart=cart, **item_data) for item_data in items_data
        ])
        return cart

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Обновляем корзину
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Если переданы новые товары — заменяем
        if items_data is not None:
            instance.items.all().delete()
            CartItem.objects.bulk_create([
                CartItem(cart=instance, **item_data) for item_data in items_data
            ])
        return instance


# 🏠 Адреса пользователя
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


# 🛍 Позиции заказа
class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно быть не меньше 1.")
        return value


# 🛒 Заказ с вложенными позициями
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(),
        source='address',
        write_only=True
    )
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'address', 'address_id', 'comment', 'total', 'created_at', 'items']
        read_only_fields = ['user', 'created_at', 'total']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        validated_data['user'] = self.context['request'].user

        order = Order.objects.create(**validated_data)

        order_items = []
        total = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            ))
            total += product.price * quantity

        OrderItem.objects.bulk_create(order_items)
        order.total = total
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            order_items = []
            total = 0
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                order_items.append(OrderItem(
                    order=instance,
                    product=product,
                    quantity=quantity,
                    price=product.price
                ))
                total += product.price * quantity
            OrderItem.objects.bulk_create(order_items)
            instance.total = total
            instance.save()

        return instance