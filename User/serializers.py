from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP, Notification, UserBonus, BonusTransaction

User = get_user_model()

# ==============================
# Регистрация
# ==============================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "confirm_password"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        otp = OTP.create_otp(user, purpose="registration")
        return {"user": user, "otp": otp.code}


# ==============================
# Проверка OTP
# ==============================
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")

        try:
            otp = OTP.objects.filter(
                user=user,
                code=data["code"],
                is_used=False,
                purpose="registration"
            ).latest("created_at")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Неверный код")

        if otp.is_expired():
            raise serializers.ValidationError("Код просрочен")

        data["user"] = user
        data["otp"] = otp
        return data

    def save(self):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]
        user.is_verified = True
        user.save()
        otp.is_used = True
        otp.save()
        return user


# ==============================
# Повторная отправка OTP
# ==============================
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        if user.is_verified:
            raise serializers.ValidationError("Email уже подтверждён")
        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        otp = OTP.create_otp(user, purpose="registration")
        return {"user": user, "otp": otp.code}


# ==============================
# Логин
# ==============================
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# ==============================
# Сброс пароля
# ==============================
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        otp = OTP.create_otp(user, purpose="reset_password")
        return {"user": user, "otp": otp.code}


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Пароли не совпадают")
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        try:
            otp = OTP.objects.filter(
                user=user,
                code=data["code"],
                is_used=False,
                purpose="reset_password"
            ).latest("created_at")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Неверный код")
        if otp.is_expired():
            raise serializers.ValidationError("Код просрочен")
        data["user"] = user
        data["otp"] = otp
        return data

    def save(self):
        user = self.validated_data["user"]
        otp = self.validated_data["otp"]
        user.set_password(self.validated_data["password"])
        user.save()
        otp.is_used = True
        otp.save()
        return user


# ==============================
# Обновление профиля
# ==============================
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone_number"]


# ==============================
# Пользователь
# ==============================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "phone_number", "is_verified"]


# ==============================
# Бонусы
# ==============================
class UserBonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBonus
        fields = ["total_points"]


class BonusTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BonusTransaction
        fields = ["id", "points", "transaction_type", "description", "qr_code", "created_at"]


# ==============================
# Уведомления
# ==============================
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "message", "created_at", "is_read"]
