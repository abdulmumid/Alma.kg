from django.db import models
from django.conf import settings
from Product.models import Product  # импорт твоей модели Product

User = settings.AUTH_USER_MODEL


class DeliveryRegion(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    region = models.ForeignKey(DeliveryRegion, on_delete=models.CASCADE, related_name="addresses")
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=50)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.region.name}, {self.street}, {self.house}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "В обработке"),
        ("confirmed", "Подтвержден"),
        ("delivered", "Доставлен"),
        ("canceled", "Отменен"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    region = models.ForeignKey(DeliveryRegion, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ №{self.id} — {self.user}"


class CartItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
        return self.product.final_price * self.quantity

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"
