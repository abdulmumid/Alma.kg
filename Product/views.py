from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Product, Category_Product, UserBonus
from .serializers import ProductSerializer, CategoryProductSerializer, SimpleProductSerializer

class CategoryProductViewSet(viewsets.ModelViewSet):
    queryset = Category_Product.objects.all()
    serializer_class = CategoryProductSerializer
    permission_classes = [permissions.AllowAny]

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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def purchase(self, request, pk=None):
        product = self.get_object()
        user = request.user

        points = product.bonus_points or 0
        if points > 0:
            user_bonus, created = UserBonus.objects.get_or_create(user=user)
            user_bonus.add_points(points, description=f"Покупка {product.name}")

        total_points = getattr(user, 'bonus', None)
        total_points = total_points.total_points if total_points else 0

        return Response({
            "message": f"Вы купили {product.name}, начислено {points} бонусов",
            "total_bonus": total_points
        })
