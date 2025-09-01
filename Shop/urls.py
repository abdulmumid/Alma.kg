from django.urls import path
from .views import (
    CartView,
    AddToCartView,
    RemoveFromCartView,
    CreateOrderView,
    DeliveryRegionListView
)

urlpatterns = [
    # Получить активную корзину пользователя
    path("cart/", CartView.as_view(), name="cart-detail"),

    # Добавить товар в корзину
    path("cart/add/", AddToCartView.as_view(), name="cart-add"),

    # Удалить товар из корзины по ID элемента корзины
    path("cart/remove/<int:pk>/", RemoveFromCartView.as_view(), name="cart-remove"),

    # Создать заказ
    path("order/create/", CreateOrderView.as_view(), name="order-create"),

    # Получить список регионов доставки
    path("delivery-regions/", DeliveryRegionListView.as_view(), name="delivery-region-list"),
]
