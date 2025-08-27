from rest_framework import serializers
from .models import Category_Product, Product

# 📦 Категория продукта
class CategoryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category_Product
        fields = ['id', 'name', 'slug']


# 🛍️ Полный продукт с категорией и бонусами
class ProductSerializer(serializers.ModelSerializer):
    category = CategoryProductSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'category', 'price', 'discount', 'final_price',
            'image', 'barcode', 'bonus_points', 'is_featured', 'store', 'created_at', 'updated_at'
        ]


# 🍭 Упрощённый продукт (для листинга)
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'bonus_points']
