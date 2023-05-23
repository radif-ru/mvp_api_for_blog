import os

from django.core.management.base import BaseCommand

from .add_users import Command as AddUsers


class Command(BaseCommand):
    help = 'Сборка всех подготовленных данных'

    def handle(self, *args, **options):
        self.migrate()
        self.collect_static()

        AddUsers.create_admin()

    @staticmethod
    def migrate():
        """Подготовка и выполнение миграций"""
        os.system('python manage.py makemigrations --noinput')
        os.system('python manage.py migrate --noinput')

    @staticmethod
    def collect_static():
        """Сборка стандартных и подготовленных статических файлов"""
        os.system('mkdir static')
        os.system('python manage.py collectstatic --no-input --clear')
