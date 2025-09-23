from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from Product.models import Product
from User.models import DeliveryAddress, UserBonus

User = settings.AUTH_USER_MODEL

class Store(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="store", verbose_name=_("Владелец"))
    name = models.CharField(_("Название магазина"), max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Магазин")
        verbose_name_plural = _("Магазины")

    def __str__(self):
        return self.name


class DeliveryRegion(models.Model):
    name = models.CharField(_("Регион"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("Регион доставки")
        verbose_name_plural = _("Регионы доставки")

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", verbose_name=_("Пользователь"))
    is_active = models.BooleanField(_("Активная корзина"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Корзина")
        verbose_name_plural = _("Корзины")
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=models.Q(is_active=True), name='unique_active_cart_per_user')
        ]

    def __str__(self):
        return f"Корзина {self.user.email} ({'активна' if self.is_active else 'закрыта'})"

    @property
    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    @classmethod
    def get_or_create_cart(cls, user):
        cart = cls.objects.filter(user=user, is_active=True).first()
        if not cart:
            cart = cls.objects.create(user=user)
        return cart


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name=_("Корзина"))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Продукт"))
    quantity = models.PositiveIntegerField(_("Количество"), default=1)

    class Meta:
        verbose_name = _("Товар в корзине")
        verbose_name_plural = _("Товары в корзине")

    def get_total_price(self):
        return self.product.final_price * self.quantity

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", _("В обработке")),
        ("confirmed", _("Подтвержден")),
        ("delivered", _("Доставлен")),
        ("canceled", _("Отменен")),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Пользователь"))
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name="order", verbose_name=_("Корзина"))
    address = models.ForeignKey(DeliveryAddress, on_delete=models.CASCADE, verbose_name=_("Адрес доставки"))
    total_price = models.DecimalField(_("Сумма заказа"), max_digits=10, decimal_places=2, default=0)
    used_bonus_points = models.PositiveIntegerField(_("Использованные бонусы"), default=0)
    status = models.CharField(_("Статус"), max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f"Заказ №{self.id} — {self.user.email}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        if self.cart:
            total = self.cart.total_price

            # Списание бонусов
            if self.used_bonus_points > 0:
                bonus_obj, _ = UserBonus.objects.get_or_create(user=self.user)
                points_to_use = min(self.used_bonus_points, bonus_obj.total_points)
                if points_to_use > 0:
                    bonus_obj.spend_points(points_to_use, description=f"Списание при заказе №{self.id}")
                    total -= points_to_use

            self.total_price = max(total, 0)

        super().save(*args, **kwargs)

        if is_new and self.cart:
            # Начисляем бонусы за каждый товар
            for item in self.cart.items.all():
                item.product.award_bonus_to_user(self.user)

            # Закрываем корзину
            self.cart.is_active = False
            self.cart.save()
