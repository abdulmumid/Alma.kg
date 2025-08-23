from rest_framework import viewsets, permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .serializers import *
from .models import *
from Product.models import Product
from Product.serializers import ProductSerializer


# 📈 Доска (только чтение)
class BoardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Board.objects.all().order_by('-created_at')
    serializer_class = BoardSerializer
    permission_classes = [permissions.AllowAny]


# 📍 Магазины — фильтр по геолокации и радиусу
class StoreListView(generics.ListAPIView):
    serializer_class = StoreSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = Store.objects.all()
        lat = self.request.query_params.get("lat")
        lon = self.request.query_params.get("lon")
        radius = self.request.query_params.get("radius") 

        if lat and lon:
            try:
                user_location = Point(float(lon), float(lat), srid=4326)
            except ValueError:
                return Store.objects.none()

            qs = qs.annotate(distance=Distance("location", user_location)).order_by("distance")
            if radius:
                qs = qs.filter(location__distance_lte=(user_location, float(radius) * 1000))
        return qs


# 📍 Ближайший магазин
class NearestStoreView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            lat = float(request.query_params.get('lat'))
            lon = float(request.query_params.get('lon'))
        except (TypeError, ValueError):
            return Response({'error': 'Некорректные координаты'}, status=status.HTTP_400_BAD_REQUEST)

        user_location = Point(lon, lat, srid=4326)
        nearest = Store.objects.annotate(distance=Distance('location', user_location)).order_by('distance').first()

        if not nearest:
            return Response({'error': 'Магазины не найдены'}, status=status.HTTP_404_NOT_FOUND)

        data = StoreSerializer(nearest).data
        data['distance_km'] = round(nearest.distance.km, 2)
        return Response(data)


# 🎯 Акции
class StockViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stock.objects.all().order_by('-created_at')
    serializer_class = StockSerializer
    permission_classes = [permissions.AllowAny]


# 📢 Сторисы
class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all().order_by('-created_at')
    serializer_class = StorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ⚡ Срочная покупка
class HurryBuyViewSet(viewsets.ModelViewSet):
    queryset = HurryBuy.objects.all().order_by('-start_date')
    serializer_class = HurryBuySerializer
    permission_classes = [permissions.IsAuthenticated]


