from rest_framework import serializers
from .models import *
from Product.models import Product
from Product.serializers import ProductSerializer

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'title', 'slug', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['slug', 'created_at', 'updated_at']

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']

class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

class StoreSerializer(serializers.ModelSerializer):
    distance_km = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Store
        fields = ["id", "name", "address", "location", "is_open_24h", "working_hours", "distance_km"]

    def get_distance_km(self, obj):
        return round(obj.distance.km, 2) if hasattr(obj, "distance") else None

class HurryBuySerializer(serializers.ModelSerializer):
    class Meta:
        model = HurryBuy
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at', 'format_price']
