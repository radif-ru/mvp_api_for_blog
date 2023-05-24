from random import randint

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from blog.models import Article, Comment


class Command(BaseCommand):
    help = 'Создание комментария со случайным автором к случайной статье'

    @staticmethod
    def add_comment(text: str) -> None:
        """ Создание комментария со случайным автором к случайной статье """
        # Количество пользователей в БД
        quantity_users: int = User.objects.count()

        # Случайный пользователь из существующих в БД
        rand_user_id: int = randint(1, quantity_users)

        # Количество статей в БД
        quantity_articles: int = Article.objects.count()

        # Случайная статья из существующих в БД
        rand_article_id: int = randint(1, quantity_articles)

        if not Comment.objects.filter(text=text):
            Comment.objects.create(
                article_id=rand_article_id,
                user_id=rand_user_id,
                text=text)
