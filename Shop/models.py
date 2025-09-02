from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from Product.models import Product

User = settings.AUTH_USER_MODEL

# 🛒 Корзина
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="carts", verbose_name=_("Пользователь"))
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Дата обновления"), auto_now=True)
    is_active = models.BooleanField(_("Активная корзина"), default=True)

    class Meta:
        verbose_name = _("Корзина")
        verbose_name_plural = _("Корзины")

    def __str__(self):
        return f"Корзина {self.user} ({'активная' if self.is_active else 'закрыта'})"

    @property
    def total_price(self):
        """Сумма корзины считается автоматически."""
        return sum(item.get_total_price() for item in self.items.all())


# 🛍️ Элемент корзины
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


# 🧾 Заказ
class Order(gis_models.Model):
    STATUS_CHOICES = (
        ("pending", _("В обработке")),
        ("confirmed", _("Подтвержден")),
        ("delivered", _("Доставлен")),
        ("canceled", _("Отменен")),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name=_("Пользователь"))
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name="order", verbose_name=_("Корзина"))
    address = models.ForeignKey("User.DeliveryAddress", on_delete=models.CASCADE, verbose_name=_("Адрес доставки"))
    total_price = models.DecimalField(_("Сумма заказа"), max_digits=10, decimal_places=2, default=0)
    used_bonus_points = models.PositiveIntegerField(_("Использованные бонусы"), default=0)
    status = models.CharField(_("Статус"), max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")

    def __str__(self):
        return f"Заказ №{self.id} — {self.user}"

    def save(self, *args, **kwargs):
        """Автоматический расчёт total_price при сохранении."""
        if self.cart:
            total = self.cart.total_price
            if self.used_bonus_points:
                total -= self.used_bonus_points
                total = max(total, 0)
            self.total_price = total
        super().save(*args, **kwargs)

    def apply_bonuses(self):
        """Списание бонусов пользователя при оплате заказа."""
        user_bonus = getattr(self.user, "bonus", None)
        if user_bonus and self.used_bonus_points > 0:
            user_bonus.spend_points(points=self.used_bonus_points, description=f"Оплата заказа №{self.id}")

    def award_bonuses(self):
        """Начисление бонусов за покупку."""
        for item in self.cart.items.all():
            if hasattr(item.product, "award_bonus_to_user"):
                item.product.award_bonus_to_user(self.user)


# 🌍 Регион доставки
class DeliveryRegion(models.Model):
    name = models.CharField(_("Регион"), max_length=100, unique=True)

    class Meta:
        verbose_name = _("Регион доставки")
        verbose_name_plural = _("Регионы доставки")

    def __str__(self):
        return self.name
