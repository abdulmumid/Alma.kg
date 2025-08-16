from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .models import *
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

# Категории товаров — CRUD для всех (можно потом ограничить)
class CategoryProductViewSet(viewsets.ModelViewSet):
    queryset = Category_Product.objects.all()
    serializer_class = CategoryProductSerializer
    permission_classes = [permissions.AllowAny]


# Товары — только чтение, с фильтрацией, поиском и сортировкой
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'price': ['gte', 'lte'],
        'category': ['exact'],
    }
    search_fields = ['name']
    ordering_fields = ['price', 'name', 'created_at', 'is_featured']
    ordering = ['-created_at']


# 🛒 Корзина
class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_cart(self, user):
        return Cart.objects.get_or_create(user=user)[0]

    def list(self, request):
        cart = self._get_cart(request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product_id')
        quantity = max(int(request.data.get('quantity', 1)), 1)

        cart = self._get_cart(request.user)
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity = item.quantity + quantity if not created else quantity
        item.save()
        return Response({'message': 'Товар добавлен в корзину'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response({'error': 'Корзина не найдена'}, status=status.HTTP_404_NOT_FOUND)

        deleted, _ = CartItem.objects.filter(cart=cart, product_id=request.data.get('product_id')).delete()
        if deleted:
            return Response({'message': 'Товар удалён из корзины'})
        return Response({'error': 'Товар не найден в корзине'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            return Response({'error': 'Корзина не найдена'}, status=status.HTTP_404_NOT_FOUND)
        cart.items.all().delete()
        return Response({'message': 'Корзина очищена'})


# 🏠 Адреса
class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


# 🛍 Заказы
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# 📦 Позиции заказов
class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)
