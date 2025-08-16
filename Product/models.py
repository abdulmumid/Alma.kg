from django.db import models
from django.utils.text import slugify
from Alma.models import Store  
from django.db import models
from django.conf import settings


# Категория продуктов
class Category_Product(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("Slug", unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория продукта"
        verbose_name_plural = "Категории продуктов"


# Продукт
class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    category = models.ForeignKey(Category_Product, on_delete=models.CASCADE, verbose_name="Категория")
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    discount = models.DecimalField("Скидка %", max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    barcode = models.CharField("Штрихкод", max_length=100, unique=True)
    label = models.CharField("Начисленные бонусы", max_length=50, blank=True)
    is_featured = models.BooleanField("Избранное", default=False)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Магазин")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def final_price(self):
        if self.discount:
            return self.price * (1 - self.discount / 100)
        return self.price

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


# 🛒 Корзина
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.user}"

    def get_total(self):
        return sum(item.get_total_price() for item in self.items.select_related("product"))

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


# 📦 Товары в корзине
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество", default=1)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    def get_total_price(self):
        return self.product.price * self.quantity

    class Meta:
        unique_together = ('cart', 'product')
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"


# 📍 Адрес доставки
class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street = models.CharField("Улица", max_length=255)
    house = models.CharField("Дом", max_length=50)
    corpus = models.CharField("Корпус", max_length=50, blank=True, null=True)
    entrance = models.CharField("Подъезд", max_length=50, blank=True, null=True)
    floor = models.CharField("Этаж", max_length=50, blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"{self.street}, {self.house}" + (f" (корп. {self.corpus})" if self.corpus else "")

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"
        ordering = ["-created_at"]


# 🧾 Заказ
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    comment = models.TextField("Комментарий", blank=True)
    total = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.pk} — {self.get_status_display()} ({self.total}₽)"

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']


# 🧾 Товар в заказе
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество")
    price = models.DecimalField("Цена за единицу", max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    def get_total_price(self):
        return self.price * self.quantity

    class Meta:
        verbose_name = "Товар заказа"
        verbose_name_plural = "Товары заказа"
