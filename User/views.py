from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer, VerifyEmailSerializer, LoginSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer, ProfileUpdateSerializer
)


# POST /api/auth/register
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RegisterSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "Регистрация создана. Проверьте email для кода."}, status=201)


# POST /api/auth/verify
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = VerifyEmailSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.save()
        # при успешной верификации можно сразу выдать токен
        refresh = RefreshToken.for_user(user)
        return Response({
            "detail": "Email подтверждён",
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })


# POST /api/auth/login
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = s.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)})


# POST /api/auth/forgot
class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = ForgotPasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        return Response({"detail": "Код отправлен на email"})


# POST /api/auth/reset
class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = ResetPasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "Пароль обновлён"})


# GET/PATCH /api/profile
class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = {
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "phone": request.user.phone,
            "qr_payload": request.user.qr_payload,
            "qr_code": request.build_absolute_uri(request.user.qr_code.url) if request.user.qr_code else None,
        }
        return Response(data)

    def patch(self, request):
        s = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
        return Response({"detail": "Профиль обновлён"})
