from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.files.base import ContentFile
from io import BytesIO
from uuid import uuid4
import qrcode
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


# --- Менеджер пользователя ---
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError(_("Email обязателен"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        # Суперпользователь активируется отдельно в create_superuser
        user.is_active = extra.get("is_active", False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("is_active", True)  # ✅ суперюзер сразу активен (без верификации)
        if extra.get("is_staff") is not True or extra.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_staff=True and is_superuser=True"))
        user = self.create_user(email, password, **extra)
        return user


# --- Модель пользователя ---
def generate_qr_payload():
    return uuid4().hex

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(_("Электронная почта"), unique=True)
    phone       = PhoneNumberField(_("Телефон"), blank=True, null=True)
    first_name  = models.CharField(_("Имя"), max_length=50, blank=True)
    last_name   = models.CharField(_("Фамилия"), max_length=50, blank=True)

    is_active   = models.BooleanField(_("Активен"), default=False)
    is_staff    = models.BooleanField(_("Сотрудник"), default=False)
    date_joined = models.DateTimeField(_("Дата регистрации"), default=timezone.now)

    qr_payload  = models.CharField(_("QR Payload"), max_length=64, unique=True, default=generate_qr_payload)
    qr_code     = models.ImageField(_("QR Код"), upload_to="qr_codes/", blank=True, null=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.qr_code:
            img = qrcode.make(self.qr_payload)
            buf = BytesIO()
            img.save(buf, format="PNG")
            self.qr_code.save(f"{self.qr_payload}.png", ContentFile(buf.getvalue()), save=False)
        super().save(*args, **kwargs)


# --- Коды подтверждения/сброса ---
class Verification(models.Model):
    class Purpose(models.TextChoices):
        REGISTER = "register", _("Регистрация")
        RESET    = "reset",    _("Сброс пароля")

    user       = models.ForeignKey(CustomUser, verbose_name=_("Пользователь"),
                                   on_delete=models.CASCADE, related_name="verifications")
    purpose    = models.CharField(_("Цель"), max_length=16, choices=Purpose.choices)
    code       = models.CharField(_("Код"), max_length=6)  # не делаем global unique — достаточно пары (user, code)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    is_used    = models.BooleanField(_("Использован"), default=False)

    class Meta:
        verbose_name = _("Код подтверждения")
        verbose_name_plural = _("Коды подтверждения")
        indexes = [models.Index(fields=["user", "purpose", "code"])]

    def __str__(self):
        return f"{self.user.email} [{self.purpose}] {self.code}"

    # TTL 24 часа
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)

    # Отправка письма
    def send_email(self):
        subj = _("Подтверждение регистрации") if self.purpose == self.Purpose.REGISTER else _("Восстановление пароля")
        msg  = _("Ваш код: %(code)s. Срок действия 24 часа.") % {"code": self.code}
        send_mail(subj, msg, None, [self.user.email])


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