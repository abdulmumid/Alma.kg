from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from User.models import CustomUser, Verification


class Command(BaseCommand):
    help = "Удаляет аккаунты, не подтвердившие email за 24 часа"

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        deleted = 0

        candidates = CustomUser.objects.filter(is_active=False)

        for user in candidates:
            regs = Verification.objects.filter(user=user, purpose=Verification.Purpose.REGISTER)
            try:
                earliest_reg = regs.earliest("created_at")
            except Verification.DoesNotExist:
                continue

            if not regs.filter(is_used=True).exists() and earliest_reg.created_at < cutoff:
                with transaction.atomic():
                    user_email = user.email
                    user.delete()
                    deleted += 1
                    self.stdout.write(f"Удалён пользователь: {user_email}")

        self.stdout.write(self.style.SUCCESS(f"Всего удалено: {deleted}"))
