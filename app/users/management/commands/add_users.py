from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import OperationalError, ProgrammingError


class Command(BaseCommand):
    help = 'Создание админа и пользователей'

    def handle(self, *args, **options):
        """Команды на выполнение"""
        self.create_admin()

    @staticmethod
    def create_admin() -> None:
        """ Создание супер-юзера """
        try:
            if not User.objects.filter(username='admin'):
                User.objects.create_superuser(
                    username='admin',
                    password='qwertytwerq')
        except OperationalError or ProgrammingError as error:
            print(f'\n{error}\n')
