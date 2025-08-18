# config/urls.py
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static

# 📌 Swagger документация
schema_view = get_schema_view(
    openapi.Info(
        title="Alma API",
        default_version='v1',
        description="Документация API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),

    # Документация API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # API приложения с разными префиксами
    path('api/alma/', include('Alma.urls')), 
    path('api/user/', include('User.urls')),   
    path('api/product/', include('Product.urls')),
]

# 📌 Настройки медиа-файлов (только в DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
