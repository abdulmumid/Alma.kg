from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    RemoveFromCartView,
    CreateOrderView,
    DeliveryRegionListView
)

urlpatterns = [
    # Корзина
    path("cart/", CartView.as_view(), name="cart-detail"),
    path("cart/add/", AddToCartView.as_view(), name="cart-add"),
    path("cart/remove/<int:pk>/", RemoveFromCartView.as_view(), name="cart-remove"),

    # Заказ
    path("order/create/", CreateOrderView.as_view(), name="order-create"),

    # Регионы доставки
    path("delivery-regions/", DeliveryRegionListView.as_view(), name="delivery-region-list"),
]
