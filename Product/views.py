from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from .models import Product, Category_Product, UserBonus
from .serializers import ProductSerializer, CategoryProductSerializer, SimpleProductSerializer

# ==============================
# Категории продуктов
# ==============================
class CategoryProductViewSet(viewsets.ModelViewSet):
    queryset = Category_Product.objects.all()
    serializer_class = CategoryProductSerializer
    permission_classes = [permissions.AllowAny]
    swagger_tags = ["Категории"]


# ==============================
# Продукты
# ==============================
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
    swagger_tags = ["Товары"]

    # ------------------------------
    # Начисление бонусов пользователю
    # ------------------------------
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def purchase(self, request, pk=None):
        product = self.get_object()
        user = request.user

        # Начисляем бонусы
        points = product.bonus_points or 0
        if points > 0:
            user_bonus, created = UserBonus.objects.get_or_create(user=user)
            user_bonus.add_points(points, description=f"Покупка {product.name}")

        return Response({
            "message": f"Вы купили {product.name}, начислено {points} бонусов",
            "total_bonus": user.bonus.total_points if hasattr(user, 'bonus') else 0
        })
