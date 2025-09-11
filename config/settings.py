import os
from pathlib import Path
from datetime import timedelta
from xml.etree.ElementInclude import include
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_filters",

    "leaflet",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "drf_yasg",
    "corsheaders",
    "ckeditor",
    "ckeditor_uploader",

    "Alma",
    "User",
    "Product",
    "Shop",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": os.getenv("DB_NAME", "alma_db"),
        "USER": os.getenv("DB_USER", "almauser"),
        "PASSWORD": os.getenv("DB_PASSWORD", "alma4231"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_USER_MODEL = "User.CustomUser"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("ACCESS_TOKEN_LIFETIME_MINUTES", 60))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("REFRESH_TOKEN_LIFETIME_DAYS", 1))),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {"default": {"toolbar": "full", "height": 300, "width": "100%"}}


JAZZMIN_SETTINGS = {
    "site_title": "My Project Admin",
    "site_header": "My Project",
    "site_brand": "My Project",
    "show_sidebar": True,
    "navigation_expanded": True,
    "show_ui_builder": True,
    "icons": {
        # Приложение alma
        "alma.board": "dashboard",
        "alma.stock": "local_offer",
        "alma.story": "history",
        "alma.store": "store",
        "alma.hurrybuy": "flash_on",

        # Приложение product
        "product.category_product": "category",
        "product.product": "inventory_2",

        # Приложение shop
        "shop.cart": "shopping_cart",
        "shop.cartitem": "add_shopping_cart",
        "shop.order": "receipt_long",
        "shop.orderitem": "inventory_2",
        "shop.address": "location_on",
        "shop.deliveryregion": "place",

        # Приложение user
        "user.customuser": "person",
        "user.otp": "vpn_key",
        "user.userbonus": "star",
        "user.bonustransaction": "monetization_on",
        "user.notification": "notifications",
        "user.deliveryaddress": "place"
    },
    "custom_css": None,
    "custom_js": None,
}

USE_CONSOLE_EMAIL = os.getenv("USE_CONSOLE_EMAIL", "True").lower() in ("true", "1", "t")

if USE_CONSOLE_EMAIL:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@supermarket.com")
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
    EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
    DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER)

CORS_ALLOW_ALL_ORIGINS = True


ONESIGNAL_APP_ID = "4ba04319-622f-42cd-bfeb-01ca69d7c9d8"
ONESIGNAL_API_KEY = "os_v2_app_joqegglcf5bm3p7lahfgtv6j3dzgyaqkvyqepluk6lekwm3idp2vi77hv5wdmmk75olna6cfza3dftdvfrnjxfxwwobwc44cgqukdui"
