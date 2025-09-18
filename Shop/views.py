from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, DeliveryRegion
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, DeliveryRegionSerializer

# ================= Активная корзина =================
class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        return cart


# ================= Добавление товара в корзину =================
class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)
        # Проверяем, есть ли уже этот товар в корзине
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()


# ================= Удаление товара из корзины =================
class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        return cart.items.all()


# ================= Создание заказа =================
class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        serializer = self.get_serializer(data={
            "user": request.user.id,
            "cart": cart.id,
            "address": request.data.get("address"),
            "used_bonus_points": int(request.data.get("used_bonus_points", 0))
        })
        serializer.is_valid(raise_exception=True)
        order = serializer.save()  # Order.save() уже закрывает корзину, очищает товары и начисляет бонусы
        order.apply_bonuses()      # Начисление бонусов 5% от суммы заказа, если нужно
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)


# ================= Список регионов доставки =================
class DeliveryRegionListView(generics.ListAPIView):
    queryset = DeliveryRegion.objects.all()
    serializer_class = DeliveryRegionSerializer
    permission_classes = [IsAuthenticated]
