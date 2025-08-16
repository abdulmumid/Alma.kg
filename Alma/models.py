from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django.contrib.gis.db import models as geomodels
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone

# 📌 Доска
class Board(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", unique=True, blank=True)
    description = RichTextUploadingField("Описание")
    image = models.ImageField("Изображение", upload_to='boards/')
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Доска"
        verbose_name_plural = "Доски"
        ordering = ["-created_at"]


# 📌 Магазин
class Store(geomodels.Model):
    name = models.CharField("Название магазина", max_length=255)
    address = models.CharField("Адрес", max_length=255)
    location = geomodels.PointField("Координаты (широта, долгота)", geography=True)
    is_open_24h = models.BooleanField("Круглосуточно", default=False)
    working_hours = models.CharField("Часы работы", max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} — {self.address}"

    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"
        ordering = ["name"]


# 📌 Акция
class Stock(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to='stock/')
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ["-created_at"]


# 📌 Сторис
class Story(models.Model):
    title = models.CharField("Заголовок", max_length=100)
    icon = models.ImageField("Иконка", upload_to='stories/')
    is_active = models.BooleanField("Активно", default=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    def __str__(self):
        return f"{self.title} {'✅' if self.is_active else '❌'}"

    class Meta:
        verbose_name = "Сторис"
        verbose_name_plural = "Сторисы"
        ordering = ["-created_at"]


# ⚡ Срочная покупка
class HurryBuy(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    description = models.TextField("Описание")
    price = models.DecimalField("Цена", max_digits=8, decimal_places=2)
    format_price = models.CharField("Форматированная цена", max_length=255, blank=True, null=True)
    percent_discount = models.DecimalField("Процент скидки", max_digits=5, decimal_places=2, blank=True, null=True)
    image = models.ImageField("Изображение", upload_to='hurry_buy/')
    start_date = models.DateTimeField("Начало")
    end_date = models.DateTimeField("Окончание")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    @property
    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValueError("Дата окончания должна быть позже даты начала")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Срочная покупка"
        verbose_name_plural = "Срочные покупки"
        ordering = ["-start_date"]


# 🔔 Уведомления
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField("Сообщение")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.user} — {'✔' if self.is_read else '✖'}"

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]
