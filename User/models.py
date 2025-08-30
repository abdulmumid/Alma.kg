from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import random
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _

User = settings.AUTH_USER_MODEL

# Менеджер пользователя
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


# Пользовательская модель
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

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


# OTP модель
class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("registration", "Регистрация"),
        ("reset_password", "Сброс пароля"),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default="registration")
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

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
        return cls.objects.create(user=user, code=code, purpose=purpose)


# Баланс пользователя
class UserBonus(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bonus')
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.email} - {self.total_points} бонусов"

    def add_points(self, points, description="", qr_code=None):
        self.total_points += points
        self.save()
        BonusTransaction.objects.create(
            user=self.user,
            points=points,
            transaction_type='earned',
            description=description,
            qr_code=qr_code
        )

    def spend_points(self, points, description="", qr_code=None):
        if points > self.total_points:
            raise ValueError("Недостаточно бонусов")
        self.total_points -= points
        self.save()
        BonusTransaction.objects.create(
            user=self.user,
            points=points,
            transaction_type='spent',
            description=description,
            qr_code=qr_code
        )


# История начислений/списаний
class BonusTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('earned', 'Начислено'),
        ('spent', 'Потрачено'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bonus_transactions')
    points = models.PositiveIntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_code = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        action = "начислено" if self.transaction_type == "earned" else "потрачено"
        return f"{self.user.email} - {self.points} бонусов {action}"


# Модель уведомлений
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = RichTextUploadingField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Уведомление для {self.user.email} — {'✔' if self.is_read else '✖'}"



class DeliveryAddress(gis_models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    region = gis_models.ForeignKey("Shop.DeliveryRegion", on_delete=models.CASCADE, related_name="addresses")
    street = models.CharField(max_length=255)
    house = models.CharField(max_length=50)
    location = gis_models.PointField(geography=True, null=True, blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street}, {self.house} ({self.region.name})"
