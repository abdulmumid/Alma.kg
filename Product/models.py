# Product/models.py
from django.db import models
from django.utils.text import slugify
from Alma.models import Store
from django.conf import settings
from User.models import UserBonus, BonusTransaction  # импортируем бонусы

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


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    category = models.ForeignKey(Category_Product, on_delete=models.CASCADE, verbose_name="Категория")
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    discount = models.DecimalField("Скидка %", max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    barcode = models.CharField("Штрихкод", max_length=100, unique=True)
    bonus_points = models.PositiveIntegerField("Бонусы за покупку", default=0)  # добавили поле бонусов
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

    def award_bonus_to_user(self, user):
        if self.bonus_points > 0:
            user_bonus, created = UserBonus.objects.get_or_create(user=user)
            user_bonus.add_points(
                points=self.bonus_points,
                description=f"Бонус за покупку продукта: {self.name}"
            )
