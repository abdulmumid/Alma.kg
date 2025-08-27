from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView,
    VerifyEmailOTPView,
    ResendOTPView,
    ResetPasswordView,
    ResetPasswordConfirmView,
    UpdateUserView,
    DeleteAccountView,
    NotificationViewSet,
)

urlpatterns = [
    # Регистрация
    path("register/", RegisterView.as_view(), name="register"),

    # Подтверждение email по коду OTP
    path("verify/", VerifyEmailOTPView.as_view(), name="verify-email-otp"),

    # Повторная отправка OTP
    path("resend-otp/", ResendOTPView.as_view(), name="resend-otp"),

    # Авторизация JWT
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Сброс пароля через OTP
    path("password-reset/", ResetPasswordView.as_view(), name="password-reset-otp"),
    path("password-reset-confirm/", ResetPasswordConfirmView.as_view(), name="password-reset-confirm-otp"),

    # Управление аккаунтом
    path("update/", UpdateUserView.as_view(), name="update-account"),
    path("delete/", DeleteAccountView.as_view(), name="delete-account"),

    # Уведомления
    path("notifications/", NotificationViewSet.as_view(), name="user-notifications"),
]
