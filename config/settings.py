import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Базовая директория
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ (лучше хранить в .env)
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-38!s$7g@0o!2zxt1r9q1^e4b@r-9fxt9%=g+9v5t@v#zr$@8x*")

# Режим дебага
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Разрешённые хосты
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")


# ==========================
# 📌 Приложения
# ==========================
INSTALLED_APPS = [
    # UI
    "jazzmin",

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",

    # Библиотеки
    "django_filters",
    "leaflet",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "drf_yasg",
    "corsheaders",
    "ckeditor",
    "ckeditor_uploader",

    # Локальные приложения
    "Alma",
    "User",
    "Product",
]


# ==========================
# 📌 Middleware
# ==========================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # должно быть первым для CORS
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ==========================
# 📌 URL / WSGI
# ==========================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"


# ==========================
# 📌 База данных
# ==========================
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


# ==========================
# 📌 Шаблоны
# ==========================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # папка для шаблонов
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # важно для админки
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ==========================
# 📌 Аутентификация
# ==========================
AUTH_USER_MODEL = "User.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ==========================
# 📌 DRF + JWT
# ==========================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ==========================
# 📌 Локализация
# ==========================
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True


# ==========================
# 📌 Статика и медиа
# ==========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ==========================
# 📌 CKEditor
# ==========================
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 300,
        "width": "100%",
    },
}


# ==========================
# 📌 Jazzmin (админка)
# ==========================
JAZZMIN_SETTINGS = {
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "API.Board": "fas fa-clipboard",
    },
}


# ==========================
# 📌 Почта (замени на свои)
# ==========================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@supermarket.com"


# ==========================
# 📌 CORS
# ==========================
CORS_ALLOW_ALL_ORIGINS = True


# ==========================
# 📌 ID для моделей
# ==========================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
