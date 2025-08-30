from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, Order, DeliveryRegion
from .serializers import CartSerializer, CartItemSerializer, DeliveryRegionSerializer, OrderSerializer


class CartView(generics.RetrieveAPIView):
    """Получить активную корзину пользователя"""
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        return cart


class AddToCartView(generics.CreateAPIView):
    """Добавить товар в корзину"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        cart, created = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        serializer.save(cart=cart)


class RemoveFromCartView(generics.DestroyAPIView):
    """Удалить товар из корзины"""
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user, is_active=True)
        return cart.items.all()


class CreateOrderView(generics.CreateAPIView):
    """Оформить заказ"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user, is_active=True)
        address_id = request.data.get("address")
        used_bonus = request.data.get("used_bonus_points", 0)

        order = Order.objects.create(
            user=request.user,
            cart=cart,
            address_id=address_id,
            used_bonus_points=used_bonus
        )

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeliveryRegionListView(generics.ListAPIView):
    """Список регионов доставки"""
    queryset = DeliveryRegion.objects.all()
    serializer_class = DeliveryRegionSerializer
    permission_classes = [IsAuthenticated]