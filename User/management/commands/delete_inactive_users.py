from django.core.management.base import BaseCommand
from django.utils import timezone
from User.models import CustomUser, Verification


class Command(BaseCommand):
    help = "Удаляет аккаунты, не подтвердившие email за 24 часа"

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timezone.timedelta(hours=24)
        # Находим пользователей, у которых НЕТ использованной регистрации и все их регистрации старше 24ч
        candidates = CustomUser.objects.filter(is_active=False)
        deleted = 0
        for u in candidates:
            regs = Verification.objects.filter(user=u, purpose=Verification.Purpose.REGISTER)
            if regs.exists() and not regs.filter(is_used=True).exists() and regs.earliest("created_at").created_at < cutoff:
                u.delete()
                deleted += 1
        self.stdout.write(self.style.SUCCESS(f"Удалено: {deleted}"))
