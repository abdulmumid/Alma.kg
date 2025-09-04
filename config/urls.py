from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

schema_view = get_schema_view(
    openapi.Info(
        title="Alma API",
        default_version='v1',
        description=(
    "Alma.kg — мобильное приложение для онлайн-шопинга в сети супермаркетов Alma.\n\n"
    "Наша миссия — сделать процесс покупок быстрым, удобным и выгодным для каждого клиента.\n"
    "Главная цель — предоставить полный ассортимент товаров, акции, бонусы и удобные способы доставки прямо до двери.\n\n"
    "### 📦 Основные модули и модели:\n"
    "- 🏬 **Store** — информация о магазинах Alma, их адреса, координаты и часы работы\n"
    "- 📌 **Board** — информационные доски для промо и категорий\n"
    "- 📰 **Stock** — текущие акции и предложения\n"
    "- 📸 **Story** — сторис и промо-блоки\n"
    "- ⚡ **HurryBuy** — срочные покупки с ограниченной по времени скидкой\n"
    "- 🏷 **Category_Product** — категории продуктов\n"
    "- 🍱 **Product** — продукты с ценой, скидкой, бонусами и привязкой к магазину\n"
    "- 🛒 **Cart** — корзина пользователя, активная или закрытая\n"
    "- 🛍️ **CartItem** — элемент корзины с продуктом и количеством\n"
    "- 🧾 **Order** — заказ пользователя, со статусом, суммой, бонусами и адресом доставки\n"
    "- 🌍 **DeliveryRegion** — регионы доставки\n"
    "- 👤 **CustomUser** — профиль пользователя с email, телефоном, именем, фамилией\n"
    "- 🔑 **OTP** — одноразовые коды для регистрации и сброса пароля\n"
    "- ⭐ **UserBonus** — бонусные баллы пользователя\n"
    "- 💳 **BonusTransaction** — история начисления и списания бонусов\n"
    "- 📩 **Notification** — уведомления для пользователей\n"
    "- 🏠 **DeliveryAddress** — адреса доставки с улицей, домом, регионом и координатами\n\n"
    "### 🧰 Технологии:\n"
    "- Django, Django REST Framework\n"
    "- PostgreSQL / PostGIS для геолокации\n"
    "- CKEditor для RichText полей\n"
    "- Swagger (drf-yasg) для тестирования API\n\n"
    "Все эндпоинты доступны через интерфейс Swagger, где их можно тестировать и изучать структуру данных."
)


    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('api/alma/', include('Alma.urls')), 
    path('api/user/', include('User.urls')),   
    path('api/product/', include('Product.urls')),
    path('api/shop/', include('Shop.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
