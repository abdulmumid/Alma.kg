from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, VerifyOTPView, ResendOTPView, LoginView,
    ResetPasswordView, ResetPasswordConfirmView,
    UserMeView, UserUpdateProfileView, UserDeleteAccountView,
    NotificationListCreateView, NotificationRetrieveUpdateDeleteView,
    UserBonusView, BonusTransactionListView, DeliveryAddressViewSet
)

# Router для DeliveryAddress
router = DefaultRouter()
router.register(r'addresses', DeliveryAddressViewSet, basename='addresses')

urlpatterns = [
    # --- Auth endpoints ---
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("auth/reset-password-confirm/", ResetPasswordConfirmView.as_view(), name="reset-password-confirm"),

    # --- User endpoints ---
    path("user/me/", UserMeView.as_view(), name="user-me"),
    path("user/update-profile/", UserUpdateProfileView.as_view(), name="update-profile"),
    path("user/delete-account/", UserDeleteAccountView.as_view(), name="delete-account"),

    # --- User Bonus endpoints ---
    path("user/bonus/", UserBonusView.as_view(), name="user-bonus"),
    path("user/bonus/transactions/", BonusTransactionListView.as_view(), name="bonus-transactions"),

    # --- Notifications endpoints ---
    path("notifications/", NotificationListCreateView.as_view(), name="notifications-list-create"),
    path("notifications/<int:pk>/", NotificationRetrieveUpdateDeleteView.as_view(), name="notifications-detail"),

    # --- Delivery addresses через router ---
    path("", include(router.urls)),
]
