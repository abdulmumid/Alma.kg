from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import Notification, OTP, UserBonus, BonusTransaction, DeliveryAddress
from .serializers import (
    RegisterSerializer, VerifyOTPSerializer, ResendOTPSerializer,
    LoginSerializer, ResetPasswordSerializer, ResetPasswordConfirmSerializer,
    UpdateUserSerializer, NotificationSerializer, UserBonusSerializer,
    BonusTransactionSerializer, DeliveryAddressSerializer, UserSerializer,
    PlayerIdSerializer
)
from .permissions import IsEmailVerified


def send_user_mail(subject, message, recipient):
    if recipient:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient])


# ------------------- Регистрация -------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp = OTP.objects.filter(user=user, purpose="registration").order_by("-created_at").first()
        send_user_mail(
            "Ваш код подтверждения",
            f"Ваш код подтверждения: {otp.code}. Никому не передавайте этот код.",
            user.email
        )

        return Response(
            {"message": "Регистрация успешна! Проверьте email для подтверждения.", "email": user.email},
            status=status.HTTP_201_CREATED
        )


# ------------------- Подтверждение OTP -------------------
class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Email подтверждён!",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


# ------------------- Повторная отправка OTP -------------------
class ResendOTPView(generics.GenericAPIView):
    serializer_class = ResendOTPSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        user = result['user']
        otp = result['otp']
        send_user_mail(
            "Ваш новый код подтверждения",
            f"Новый код подтверждения: {otp.code}. Никому не передавайте этот код.",
            user.email
        )
        return Response({"message": "Новый код отправлен на email"}, status=status.HTTP_200_OK)


# ------------------- Вход -------------------
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
            return Response({"error": "Неверный email или пароль"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_verified:
            return Response({"error": "Подтвердите email перед входом"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Успешный вход",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }, status=status.HTTP_200_OK)


# ------------------- Обновление player_id -------------------
class UpdatePlayerIdView(generics.UpdateAPIView):
    serializer_class = PlayerIdSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user


# ------------------- Сброс пароля -------------------
class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        otp = OTP.objects.filter(user=user, purpose="reset_password").order_by("-created_at").first()
        send_user_mail(
            "Код для сброса пароля",
            f"Ваш код для сброса пароля: {otp.code}. Никому не передавайте этот код.",
            user.email
        )
        return Response({"message": "Код для сброса пароля отправлен на email"}, status=status.HTTP_200_OK)


# ------------------- Подтверждение нового пароля -------------------
class ResetPasswordConfirmView(generics.GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Пароль успешно изменён"}, status=status.HTTP_200_OK)


# ------------------- Профиль пользователя -------------------
class UserMeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user


class UserUpdateProfileView(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user


class UserDeleteAccountView(generics.DestroyAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        return self.request.user

    def perform_destroy(self, instance):
        with transaction.atomic():
            OTP.objects.filter(user=instance).delete()
            UserBonus.objects.filter(user=instance).delete()
            BonusTransaction.objects.filter(user=instance).delete()
            DeliveryAddress.objects.filter(user=instance).delete()
            instance.delete()


# ------------------- Бонусы -------------------
class UserBonusView(generics.RetrieveAPIView):
    serializer_class = UserBonusSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_object(self):
        bonus, _ = UserBonus.objects.get_or_create(user=self.request.user)
        return bonus


class BonusTransactionListView(generics.ListAPIView):
    serializer_class = BonusTransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        return BonusTransaction.objects.filter(user=self.request.user).order_by("-created_at")


# ------------------- Уведомления -------------------
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


# ------------------- Адреса доставки -------------------
class DeliveryAddressViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmailVerified]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        if serializer.validated_data.get('is_default'):
            DeliveryAddress.objects.filter(user=user, is_default=True).update(is_default=False)
        serializer.save(user=user)

    def perform_update(self, serializer):
        user = self.request.user
        if serializer.validated_data.get('is_default'):
            DeliveryAddress.objects.filter(user=user, is_default=True).exclude(pk=serializer.instance.pk).update(is_default=False)
        serializer.save()
