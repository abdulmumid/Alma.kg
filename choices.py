from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = (
    ("pending", _("В обработке")),
    ("confirmed", _("Подтвержден")),
    ("delivered", _("Доставлен")),
    ("canceled", _("Отменен")),
)
