from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import Token
from utils.token import gen_token


class Command(BaseCommand):
    help = 'Создание пользователя или админа. ' \
           'Принимает аргументы: `username`, `password`, `is_superuser` ' \
           '(не обязательный, по умолчанию `False`)'

    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('password')
        parser.add_argument('is_superuser', type=bool, nargs='?',
                            default=False)

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        is_superuser = options['is_superuser']
        self.create_user(username, password, is_superuser)

    @staticmethod
    def create_user(username: str,
                    password: str,
                    is_superuser: bool = False) -> None:
        """ Создание пользователя или админа.
        :param username имя
        :param password пароль
        :param is_superuser является ли админом? По умолчанию `False`
        """
        if not User.objects.filter(username=username):
            if is_superuser:
                user: User = User.objects.create_superuser(
                    username=username,
                    password=password)
            else:
                user: User = User.objects.create_user(
                    username=username,
                    password=password)
            Token.objects.create(user_id=user.id, token=gen_token(32))
        else:
            print(f'Пользователь {username} уже добавлен в БД')
