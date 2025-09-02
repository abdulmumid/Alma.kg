from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order
from django.utils.translation import gettext_lazy as _

@receiver(post_save, sender=Order)
def send_order_email(sender, instance, created, **kwargs):
    if created:
        order = instance
        items_text = "\n".join([
            f"{item.product.name} — {item.quantity} шт. × {item.product.final_price} = {item.get_total_price()}"
            for item in order.cart.items.all()
        ])
        user_name = f"{order.user.first_name} {order.user.last_name}".strip()
        message = (
            f"Новый заказ от {user_name} ({order.user.email})\n"
            f"Район доставки: {order.address.region.name if order.address and order.address.region else '-'}\n"
            f"Адрес: {order.address}\n\n"
            f"Товары:\n{items_text}\n\n"
            f"Итого: {order.total_price:.2f} сом"
        )
        send_mail(
            subject=f"Новый заказ №{order.id}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["developerpythonman@gmail.com"],
            fail_silently=False,
        )
