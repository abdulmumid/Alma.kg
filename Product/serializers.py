from rest_framework import serializers
from .models import Category_Product, Product

class CategoryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category_Product
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class ProductSerializer(serializers.ModelSerializer):
    category = CategoryProductSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'price', 'discount', 'final_price',
            'image', 'barcode', 'bonus_points', 'is_featured', 'store', 'created_at', 'updated_at'
        ]
        read_only_fields = ['final_price', 'created_at', 'updated_at']

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'bonus_points']
