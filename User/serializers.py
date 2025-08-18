from rest_framework import serializers
from django.utils.crypto import get_random_string
from django.contrib.auth import authenticate
from .models import CustomUser, Verification


# Регистрация
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ["email", "phone", "first_name", "last_name", "password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create(self, validated):
        validated.pop("confirm_password")
        password = validated.pop("password")
        user = CustomUser.objects.create_user(**validated)
        user.set_password(password)
        user.is_active = False
        user.save()

        # код подтверждения для регистрации
        code = get_random_string(6, "0123456789")
        v = Verification.objects.create(user=user, purpose=Verification.Purpose.REGISTER, code=code)
        v.send_email()
        return user


# Подтверждение email
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code  = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data["email"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        v = Verification.objects.filter(
            user=user, purpose=Verification.Purpose.REGISTER, code=data["code"], is_used=False
        ).order_by("-created_at").first()

        if not v:
            raise serializers.ValidationError("Неверный код")
        if v.is_expired():
            raise serializers.ValidationError("Код истёк")

        data["user"] = user
        data["verification"] = v
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        v    = self.validated_data["verification"]
        v.is_used = True
        v.save()
        user.is_active = True
        user.save()
        return user


# Логин
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Неверный email или пароль")
        if not user.is_active:
            raise serializers.ValidationError("Email не подтверждён")
        data["user"] = user
        return data


# Запрос на восстановление
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = CustomUser.objects.get(email=data["email"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        code = get_random_string(6, "0123456789")
        v = Verification.objects.create(user=user, purpose=Verification.Purpose.RESET, code=code)
        v.send_email()
        return data


# Сброс пароля
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code  = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Пароли не совпадают")
        try:
            user = CustomUser.objects.get(email=data["email"])
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        v = Verification.objects.filter(
            user=user, purpose=Verification.Purpose.RESET, code=data["code"], is_used=False
        ).order_by("-created_at").first()

        if not v:
            raise serializers.ValidationError("Неверный код")
        if v.is_expired():
            raise serializers.ValidationError("Код истёк")

        data["user"] = user
        data["verification"] = v
        return data

    def save(self, **kwargs):
        user = self.validated_data["user"]
        v    = self.validated_data["verification"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        v.is_used = True
        v.save()
        return user


# Обновление профиля
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = CustomUser
        fields = ["first_name", "last_name", "phone"]
