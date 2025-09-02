from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, DeliveryRegion
from .serializers import CartSerializer, CartItemSerializer, DeliveryRegionSerializer, OrderSerializer


# 🔹 Получение активной корзины пользователя
class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        return cart


# 🔹 Добавление товара в корзину
class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        serializer.save(cart=cart)


# 🔹 Удаление товара из корзины
class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        return cart.items.all()


# 🔹 Создание заказа
class CreateOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Берём активную корзину
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        
        # Сериализуем данные заказа
        serializer = self.get_serializer(data={
            "user": request.user.id,
            "cart": cart.id,
            "address": request.data.get("address"),
            "used_bonus_points": int(request.data.get("used_bonus_points", 0))
        })
        serializer.is_valid(raise_exception=True)
        
        # Сохраняем заказ (total_price автоматически считается в модели)
        order = serializer.save()
        
        # Деактивируем корзину после создания заказа
        cart.is_active = False
        cart.save()
        
        return Response(self.get_serializer(order).data, status=status.HTTP_201_CREATED)


# 🔹 Список регионов доставки
class DeliveryRegionListView(generics.ListAPIView):
    queryset = DeliveryRegion.objects.all()
    serializer_class = DeliveryRegionSerializer
    permission_classes = [IsAuthenticated]
