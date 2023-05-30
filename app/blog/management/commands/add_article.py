from random import randint

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from blog.models import Article


class Command(BaseCommand):
    help = 'Создание статьи со случайным автором или ' \
           'с точным указанием. Если автор не указан - ' \
           'будет присвоен случайно из существующих в БД. ' \
           'Принимает аргументы: `title` (заголовки должны различаться),  ' \
           '`text`, `author_id` (не обязательный)'

    def add_arguments(self, parser):
        parser.add_argument('title', type=str)
        parser.add_argument('text', type=str)
        parser.add_argument('author_id', type=int, nargs='?', default=0)

    def handle(self, *args, **options):
        title = options['title']
        text = options['text']
        user_id = options['author_id']
        self.add_article(title, text, user_id)

    @staticmethod
    def add_article(title: str, text: str, author_id: int = 0) -> None:
        """ Создание статьи.
        :param title заголовок.
        :param text текст.
        :param author_id идентификатор автора.
        Если не указан - будет присвоен случайный из существующих в БД.
        """
        # Количество пользователей в БД
        quantity_users = User.objects.count()

        if not author_id:
            # Случайный пользователь из существующих в БД
            author_id: int = randint(1, quantity_users)
        if not Article.objects.filter(title=title):
            Article.objects.create(author_id=author_id,
                                   title=title,
                                   text=text)
        else:
            print(f'Статья {title:.50}... уже добавлена в БД')
