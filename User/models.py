from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode
from uuid import uuid4
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers
from django.core.exceptions import ValidationError
from datetime import timedelta
import random


# ==============================
# OTP (One-Time Password) модель
# ==============================
class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP для {self.user.email} — {self.code} {'(использован)' if self.is_used else ''}"

    def is_expired(self) -> bool:
        """Проверка: истёк ли OTP (10 минут)"""
        return timezone.now() > self.created_at + timedelta(minutes=10)

    @staticmethod
    def generate_code() -> str:
        """Генерация случайного 6-значного кода"""
        return f"{random.randint(100000, 999999)}"


# ==============================
# Менеджер пользователя
# ==============================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError("Пользователь должен иметь email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email, password, **extra_fields)


# ==============================
# Пользовательская модель
# ==============================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        unique=True,
        help_text="Только номера Кыргызстана (+996)"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField(blank=True, null=True)

    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    # Статусы
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    # ------------------------------
    # Валидация номера телефона KG
    # ------------------------------
    def clean(self):
        super().clean()
        if self.phone_number:
            try:
                num = phonenumbers.parse(str(self.phone_number), "KG")
                if not phonenumbers.is_valid_number(num):
                    raise ValidationError("Введите корректный номер телефона Кыргызстана (+996)")
            except phonenumbers.NumberParseException:
                raise ValidationError("Введите корректный номер телефона Кыргызстана (+996)")

    # ------------------------------
    # Генерация QR-кода при сохранении
    # ------------------------------
    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(f"user-{self.email}-{uuid4()}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f"qr_{uuid4()}.png"
            self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)


# ==============================
# Модель уведомлений
# ==============================
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField("Сообщение")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.user.email} — {'✔' if self.is_read else '✖'}"

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]
