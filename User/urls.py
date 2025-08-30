from django.urls import path
from .views import (
    RegisterView, VerifyOTPView, ResendOTPView, LoginView,
    ResetPasswordView, ResetPasswordConfirmView,
    UserMeView, UserUpdateProfileView, UserDeleteAccountView,
    NotificationListCreateView, NotificationRetrieveUpdateDeleteView,
    UserBonusView, BonusTransactionListView, DeliveryAddressViewSet
)

urlpatterns = [
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("api/auth/resend-otp/", ResendOTPView.as_view(), name="resend-otp"),
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("api/auth/reset-password-confirm/", ResetPasswordConfirmView.as_view(), name="reset-password-confirm"),

    path("api/user/me/", UserMeView.as_view(), name="user-me"),
    path("api/user/update-profile/", UserUpdateProfileView.as_view(), name="update-profile"),
    path("api/user/delete-account/", UserDeleteAccountView.as_view(), name="delete-account"),

    path("api/user/bonus/", UserBonusView.as_view(), name="user-bonus"),
    path("api/user/bonus/transactions/", BonusTransactionListView.as_view(), name="bonus-transactions"),

    path("api/notifications/", NotificationListCreateView.as_view(), name="notifications-list-create"),
    path("api/notifications/<int:pk>/", NotificationRetrieveUpdateDeleteView.as_view(), name="notifications-detail"),

    path("api/addresses/", DeliveryAddressViewSet.as_view({'get': 'list', 'post': 'create'}), name="address-list-create"),
]
