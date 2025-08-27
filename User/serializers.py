from rest_framework import serializers
from .models import CustomUser, OTP, Notification
from django.utils import timezone
from datetime import timedelta

# ==============================
# Регистрация пользователя
# ==============================
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = CustomUser
        fields = ["email", "phone_number", "first_name", "last_name", "birth_date", "password"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.is_verified = False  # пользователь ещё не подтвердил email
        user.save()
        # Создание OTP для верификации
        OTP.objects.create(user=user, code=OTP.generate_code())
        return user


# ==============================
# Верификация OTP
# ==============================
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")

        # Получаем последний OTP
        otp = OTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if not otp:
            raise serializers.ValidationError("Код подтверждения не найден")
        if otp.is_expired():
            raise serializers.ValidationError("Код подтверждения истёк")
        if otp.code != code:
            raise serializers.ValidationError("Неверный код подтверждения")
        attrs['user'] = user
        attrs['otp'] = otp
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        otp = self.validated_data['otp']
        otp.is_used = True
        otp.save()
        user.is_verified = True
        user.save()
        return user


# ==============================
# Повторная отправка OTP (1 минута)
# ==============================
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")
        self.user = user

        last_otp = OTP.objects.filter(user=user).order_by("-created_at").first()
        if last_otp and timezone.now() < last_otp.created_at + timedelta(minutes=1):
            raise serializers.ValidationError("Подождите минуту перед повторной отправкой кода")
        return email

    def save(self, **kwargs):
        otp = OTP.objects.create(user=self.user, code=OTP.generate_code())
        return otp


# ==============================
# Сброс пароля
# ==============================
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            self.user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")
        return email

    def save(self, **kwargs):
        # Создаём OTP для сброса пароля
        otp = OTP.objects.create(user=self.user, code=OTP.generate_code())
        return otp


class ResetPasswordConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")
        password = attrs.get("password")
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден")

        otp = OTP.objects.filter(user=user, is_used=False).order_by("-created_at").first()
        if not otp:
            raise serializers.ValidationError("Код не найден")
        if otp.is_expired():
            raise serializers.ValidationError("Код истёк")
        if otp.code != code:
            raise serializers.ValidationError("Неверный код")
        attrs['user'] = user
        attrs['otp'] = otp
        attrs['password'] = password
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        otp = self.validated_data['otp']
        password = self.validated_data['password']

        user.set_password(password)
        user.save()
        otp.is_used = True
        otp.save()
        return user


# ==============================
# Обновление данных пользователя
# ==============================
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "birth_date", "phone_number"]
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


# ==============================
# Удаление аккаунта
# ==============================
class DeleteUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь не найден")
        if not user.check_password(password):
            raise serializers.ValidationError("Неверный пароль")
        attrs['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user']
        user.delete()
        return user


# ==============================
# Уведомления
# ==============================
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'is_read', 'created_at']
        read_only_fields = ['user', 'is_read', 'created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
