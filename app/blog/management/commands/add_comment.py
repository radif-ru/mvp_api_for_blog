from random import randint

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from blog.models import Article, Comment


class Command(BaseCommand):
    help = 'Создание комментария со случайным автором к случайной статье ' \
           'или с точным указанием. Если пользователь или статья ' \
           'не указаны - будут присвоены случайно из существующих в БД. ' \
           'Принимает аргументы: `text`, `user_id` (не обязательный), ' \
           '`article_id` (не обязательный)'

    def add_arguments(self, parser):
        parser.add_argument('text', type=str)

    def handle(self, *args, **options):
        text = options['text']
        self.add_comment(text)

    @staticmethod
    def add_comment(text: str, user_id: int = 0, article_id: int = 0) -> None:
        """ Создание комментария со случайным автором к случайной статье.
        :param text комментарий.
        :param user_id идентификатор пользователя.
        :param article_id идентификатор статьи к которой создаётся комментарий.
        Если не указать user_id или article_id - будут присвоены случайные
        из существующих в БД
        """
        # Количество пользователей в БД
        quantity_users: int = User.objects.count()

        if not user_id:
            # Случайный пользователь из существующих в БД
            user_id: int = randint(1, quantity_users)

        if not article_id:
            # Количество статей в БД
            quantity_articles: int = Article.objects.count()

            # Случайная статья из существующих в БД
            article_id: int = randint(1, quantity_articles)

        if not Comment.objects.filter(text=text):
            Comment.objects.create(
                article_id=article_id,
                user_id=user_id,
                text=text)
        else:
            print(f'Комментарий {text:.50}... уже добавлен в БД')
