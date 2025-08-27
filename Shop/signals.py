from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@receiver(post_save, sender=Order)
def send_order_email(sender, instance, created, **kwargs):
    """
    Отправляем email администратору после оформления заказа
    """
    if created:  # только при создании нового заказа
        order = instance
        subject = f"Новый заказ №{order.id}"
        message = (
            f"Пользователь: {order.user.email}\n"
            f"Район доставки: {order.district.name}\n"
            f"Адрес: {order.address}\n"
            f"Сумма заказа: {order.total_price} сом\n\n"
            f"Спасибо за использование Alma Shop!"
        )
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # от кого
            ["developerpythonman@gmail.com"],  # куда
            fail_silently=False,
        )
