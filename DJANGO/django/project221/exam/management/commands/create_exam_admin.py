from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates superuser 'exam' if it does not exist"

    def handle(self, *args, **options):
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Изменение: автоматизация создания администратора exam
        # Зачем: задание требует пользователя админ-панели с логином exam
        user_model = get_user_model()
        if user_model.objects.filter(username="exam").exists():
            self.stdout.write(self.style.WARNING("User 'exam' already exists"))
            return
        user_model.objects.create_superuser(
            username="exam",
            email="exam@example.com",
            password="ExamPass123!",
        )
        self.stdout.write(self.style.SUCCESS("Superuser 'exam' created"))
