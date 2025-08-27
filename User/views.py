from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Notification, OTP
from .serializers import (
    RegisterSerializer, VerifyOTPSerializer, ResendOTPSerializer,
    LoginSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer,
    UpdateUserSerializer, NotificationSerializer
)
from .permissions import IsEmailVerified


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result["user"]
        otp = result["otp"]
        self.send_otp_email(user.email, otp)
        return Response({
            "message": "Регистрация успешна! Проверьте email для подтверждения.",
            "email": user.email
        }, status=status.HTTP_201_CREATED)

    def send_otp_email(self, email, otp):
        send_mail(
            "Ваш код подтверждения",
            f"Ваш код подтверждения: {otp}. Никому не передавайте этот код.",
            settings.DEFAULT_FROM_EMAIL,
            [email]
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерация токенов JWT после подтверждения
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Email подтверждён!",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result["user"]
        otp = result["otp"]
        send_mail(
            "Ваш новый код подтверждения",
            f"Новый код подтверждения: {otp}. Никому не передавайте этот код.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        return Response({"message": "Новый код отправлен на email"}, status=status.HTTP_200_OK)


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"]
        )
        if not user:
            return Response({"error": "Неверный email или пароль"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.is_verified:
            return Response({"error": "Подтвердите email перед входом"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Успешный вход",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result["user"]
        otp = result["otp"]
        send_mail(
            "Код для сброса пароля",
            f"Ваш код для сброса пароля: {otp}. Никому не передавайте этот код.",
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        return Response({"message": "Код для сброса пароля отправлен на email"}, status=status.HTTP_200_OK)


class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Пароль успешно изменён"}, status=status.HTTP_200_OK)


class UserMeView(generics.RetrieveAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user


class UserUpdateProfileView(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user


class UserDeleteAccountView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user


class NotificationListCreateView(generics.ListCreateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NotificationRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
