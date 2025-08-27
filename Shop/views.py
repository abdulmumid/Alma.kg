from rest_framework import generics, permissions
from .models import Order
from .serializers import OrderSerializer

class OrderCreateView(generics.CreateAPIView):
    """
    Создание заказа (корзины).
    Email администратору отправляется через signals.py
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
