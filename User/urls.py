from django.urls import path
from .views import (
    RegisterView, VerifyEmailView, LoginView,
    ForgotPasswordView, ResetPasswordView, ProfileView
)

urlpatterns = [
    path("auth/register", RegisterView.as_view()),
    path("auth/verify",   VerifyEmailView.as_view()),
    path("auth/login",    LoginView.as_view()),
    path("auth/forgot",   ForgotPasswordView.as_view()),
    path("auth/reset",    ResetPasswordView.as_view()),
    path("profile",       ProfileView.as_view()),
]
