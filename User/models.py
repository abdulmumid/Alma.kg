from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

# ==============================
# Менеджер пользователя
# ==============================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Пользователь должен иметь email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email, password, **extra_fields)


# ==============================
# Пользовательская модель
# ==============================
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True)
    phone_number = PhoneNumberField("Телефон", blank=True, null=True, unique=True)
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField("Фамилия", max_length=50)
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Сотрудник", default=False)
    is_verified = models.BooleanField("Email подтверждён", default=False)
    date_joined = models.DateTimeField("Дата регистрации", default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        if self.phone_number:
            try:
                num = phonenumbers.parse(str(self.phone_number), "KG")
                if not phonenumbers.is_valid_number(num):
                    raise ValidationError("Введите корректный номер телефона Кыргызстана (+996)")
            except phonenumbers.NumberParseException:
                raise ValidationError("Введите корректный номер телефона Кыргызстана (+996)")


# ==============================
# OTP модель
# ==============================
class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("registration", "Регистрация"),
        ("reset_password", "Сброс пароля"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ вместо User
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )
    code = models.CharField("Код", max_length=6)
    purpose = models.CharField("Назначение", max_length=20, choices=PURPOSE_CHOICES, default="registration")
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    is_used = models.BooleanField("Использован", default=False)

    class Meta:
        verbose_name = "OTP код"
        verbose_name_plural = "OTP коды"

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=10)

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    @classmethod
    def create_otp(cls, user, purpose="registration"):
        code = cls.generate_code()
        otp = cls.objects.create(user=user, code=code, purpose=purpose)
        return otp  # ✅ чтобы вернуть сам объект с кодом


# ==============================
# Модель уведомлений
# ==============================
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь")
    message = models.TextField("Сообщение")
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Уведомление для {self.user.email} — {'✔' if self.is_read else '✖'}"


