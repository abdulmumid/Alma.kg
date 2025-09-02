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


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Пользователь должен иметь email"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser должен иметь is_staff=True"))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser должен иметь is_superuser=True"))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("Email"), unique=True)
    phone_number = PhoneNumberField(_("Телефон"), blank=True, null=True, unique=True)
    first_name = models.CharField(_("Имя"), max_length=50)
    last_name = models.CharField(_("Фамилия"), max_length=50)
    is_active = models.BooleanField(_("Активен"), default=True)
    is_staff = models.BooleanField(_("Персонал"), default=False)
    is_verified = models.BooleanField(_("Подтверждён"), default=False)
    date_joined = models.DateTimeField(_("Дата регистрации"), default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        if self.phone_number:
            try:
                num = phonenumbers.parse(str(self.phone_number), "KG")
                if not phonenumbers.is_valid_number(num):
                    raise ValidationError(_("Введите корректный номер телефона Кыргызстана (+996)"))
            except phonenumbers.NumberParseException:
                raise ValidationError(_("Введите корректный номер телефона Кыргызстана (+996)"))


class OTP(models.Model):
    PURPOSE_CHOICES = (
        ("registration", _("Регистрация")),
        ("reset_password", _("Сброс пароля")),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    code = models.CharField(_("Код"), max_length=6, blank=True)
    purpose = models.CharField(_("Назначение"), max_length=20, choices=PURPOSE_CHOICES, default="registration")
    created_at = models.DateTimeField(_("Создано"), auto_now_add=True)
    is_used = models.BooleanField(_("Использован"), default=False)

    class Meta:
        verbose_name = _("OTP")
        verbose_name_plural = _("OTP-коды")
        ordering = ["-created_at"]

    @property
    def expires_at(self):
        return self.created_at + timedelta(minutes=10)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def validate_code(self, code):
        return not self.is_used and not self.is_expired() and self.code == code

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    @classmethod
    def create_otp(cls, user, purpose="registration"):
        code = cls.generate_code()
        return cls.objects.create(user=user, code=code, purpose=purpose)


class UserBonus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bonus', verbose_name=_("Пользователь"))
    total_points = models.IntegerField(_("Бонусные баллы"), default=0)

    class Meta:
        verbose_name = _("Бонус пользователя")
        verbose_name_plural = _("Бонусы пользователей")

    def __str__(self):
        return f"{self.user.email} - {self.total_points} бонусов"

    @property
    def available_points(self):
        return self.total_points

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
            raise ValueError(_("Недостаточно бонусов"))
        self.total_points -= points
        self.save()
        BonusTransaction.objects.create(
            user=self.user,
            points=points,
            transaction_type='spent',
            description=description,
            qr_code=qr_code
        )


class BonusTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('earned', _("Начислено")),
        ('spent', _("Потрачено")),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bonus_transactions', verbose_name=_("Пользователь"))
    points = models.PositiveIntegerField(_("Баллы"))
    transaction_type = models.CharField(_("Тип транзакции"), max_length=10, choices=TRANSACTION_TYPE)
    description = models.CharField(_("Описание"), max_length=255, blank=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    qr_code = models.CharField(_("QR-код"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("Транзакция бонусов")
        verbose_name_plural = _("Транзакции бонусов")
        ordering = ["-created_at"]

    def __str__(self):
        action = _("начислено") if self.transaction_type == "earned" else _("потрачено")
        return f"{self.user.email} - {self.points} бонусов {action}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    message = RichTextUploadingField(_("Сообщение"))
    is_read = models.BooleanField(_("Прочитано"), default=False)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    class Meta:
        verbose_name = _("Уведомление")
        verbose_name_plural = _("Уведомления")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} — {'✔' if self.is_read else '✖'}"

    def mark_as_read(self):
        self.is_read = True
        self.save()


class DeliveryAddress(gis_models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses", verbose_name=_("Пользователь"))
    region = gis_models.ForeignKey("Shop.DeliveryRegion", on_delete=models.CASCADE, related_name="addresses", verbose_name=_("Регион"))
    street = models.CharField(_("Улица"), max_length=255)
    house = models.CharField(_("Дом"), max_length=50)
    location = gis_models.PointField(_("Локация"), geography=True, null=True, blank=True)
    is_default = models.BooleanField(_("По умолчанию"), default=False)

    class Meta:
        verbose_name = _("Адрес доставки")
        verbose_name_plural = _("Адреса доставки")

    def __str__(self):
        return f"{self.street}, {self.house} ({self.region.name})"

    def full_address(self):
        return f"{self.street}, {self.house}, {self.region.name}"
