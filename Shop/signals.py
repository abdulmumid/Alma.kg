from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(post_save, sender=Order)
def send_order_email(sender, instance, created, **kwargs):
    if created:
        order = instance
        items_text = "\n".join([
            f"{item.product.name} — {item.quantity} шт. × {item.product.final_price:.2f} = {item.get_total_price():.2f}"
            for item in order.cart.items.all()
        ])
        message = (
            f"Новый заказ от {order.user.first_name} {order.user.last_name} ({order.user.email})\n"
            f"Адрес доставки: {order.address}\n"
            f"Товары:\n{items_text}\n"
            f"Итого: {order.total_price:.2f} сом"
        )
        send_mail(
            subject=f"Новый заказ №{order.id}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["skoprpion21818@gmail.com"],
            fail_silently=False,
        )
