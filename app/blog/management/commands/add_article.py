from random import randint

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from blog.models import Article


class Command(BaseCommand):
    help = 'Создание статьи со случайным автором'

    @staticmethod
    def add_article(title: str,
                    text: str) -> None:
        """ Создание статьи со случайным автором """
        # Количество пользователей в БД
        quantity_users = User.objects.count()

        # Случайный пользователь из существующих в БД
        rand_user_id = randint(1, quantity_users)
        if not Article.objects.filter(title=title):
            Article.objects.create(
                author_id=rand_user_id,
                title=title,
                text=text)
