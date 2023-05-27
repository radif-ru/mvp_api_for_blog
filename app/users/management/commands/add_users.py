from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import Token
from utils.token import gen_token


class Command(BaseCommand):
    help = 'Создание пользователя или админа'

    @staticmethod
    def create_user(username: str,
                    password: str,
                    is_superuser: bool = False) -> None:
        """ Создание пользователя или админа """
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
